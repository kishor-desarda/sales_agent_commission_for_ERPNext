# -*- coding: utf-8 -*-
# Copyright (c) 2024, Sales Agent Commission and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt, getdate, nowdate
from frappe import _

class AgentCommissionPayment(Document):
    def validate(self):
        self.validate_commission_entries()
        self.calculate_totals()
        self.validate_bank_account()
        
    def validate_commission_entries(self):
        """Ensure all commission entries are due for payment"""
        for entry in self.commission_entries:
            commission_entry = frappe.get_doc("Agent Commission Entry", entry.commission_entry)
            if commission_entry.status != "Due":
                frappe.throw(_("Commission Entry {0} is not due for payment. Status: {1}").format(
                    entry.commission_entry, commission_entry.status))
            if commission_entry.is_paid:
                frappe.throw(_("Commission Entry {0} is already paid").format(entry.commission_entry))
    
    def calculate_totals(self):
        """Calculate total payment amount"""
        self.total_amount = sum(flt(entry.commission_amount) for entry in self.commission_entries)
        
    def validate_bank_account(self):
        """Validate bank account exists for agent"""
        if not self.agent_bank_account:
            agent = frappe.get_doc("Agent Master", self.agent)
            primary_bank = None
            for bank in agent.bank_accounts:
                if bank.is_primary:
                    primary_bank = bank
                    break
            
            if primary_bank:
                self.agent_bank_account = primary_bank.account_number
                self.bank_name = primary_bank.bank_name
                self.ifsc_code = primary_bank.ifsc_code
            else:
                frappe.throw(_("No primary bank account found for agent {0}").format(self.agent_name))
    
    def on_submit(self):
        """Mark commission entries as paid and create ledger entry"""
        self.mark_entries_as_paid()
        self.create_payment_ledger_entry()
        self.create_payment_entry()
        
    def mark_entries_as_paid(self):
        """Mark all commission entries as paid"""
        for entry in self.commission_entries:
            frappe.db.set_value("Agent Commission Entry", entry.commission_entry, {
                "is_paid": 1,
                "payment_reference": self.name,
                "payment_date": self.payment_date,
                "status": "Paid"
            })
    
    def create_payment_ledger_entry(self):
        """Create payment entry in Agent Ledger"""
        ledger_entry = frappe.get_doc({
            "doctype": "Agent Ledger Entry",
            "agent": self.agent,
            "posting_date": self.payment_date,
            "entry_type": "Payment",
            "reference_type": "Agent Commission Payment",
            "reference_name": self.name,
            "debit": 0,
            "credit": self.total_amount,
            "balance": self.get_running_balance() - self.total_amount,
            "remarks": f"Payment for {len(self.commission_entries)} commission entries"
        })
        ledger_entry.insert()
        ledger_entry.submit()
        
    def get_running_balance(self):
        """Get running balance for agent"""
        last_entry = frappe.db.sql("""
            SELECT balance 
            FROM `tabAgent Ledger Entry` 
            WHERE agent = %s 
            AND docstatus = 1
            ORDER BY creation DESC 
            LIMIT 1
        """, self.agent)
        
        return flt(last_entry[0][0]) if last_entry else 0
    
    def create_payment_entry(self):
        """Create actual payment entry in accounts"""
        if self.create_payment_entry_flag:
            payment_entry = frappe.get_doc({
                "doctype": "Payment Entry",
                "payment_type": "Pay",
                "party_type": "Supplier",  # Treating agent as supplier
                "party": self.agent,
                "party_name": self.agent_name,
                "posting_date": self.payment_date,
                "paid_amount": self.total_amount,
                "received_amount": self.total_amount,
                "reference_no": self.name,
                "reference_date": self.payment_date,
                "remarks": f"Agent Commission Payment - {self.name}"
            })
            payment_entry.insert()
            self.db_set("payment_entry", payment_entry.name)
    
    def on_cancel(self):
        """Reverse payment entries"""
        # Mark commission entries as unpaid
        for entry in self.commission_entries:
            frappe.db.set_value("Agent Commission Entry", entry.commission_entry, {
                "is_paid": 0,
                "payment_reference": None,
                "payment_date": None,
                "status": "Due"
            })
        
        # Cancel ledger entries
        frappe.db.sql("""
            UPDATE `tabAgent Ledger Entry`
            SET docstatus = 2
            WHERE reference_type = 'Agent Commission Payment'
            AND reference_name = %s
        """, self.name)

@frappe.whitelist()
def get_due_commission_entries(agent, from_date=None, to_date=None):
    """Get all due commission entries for an agent"""
    conditions = ["agent = %(agent)s", "status = 'Due'", "docstatus = 1", "is_paid = 0"]
    
    if from_date:
        conditions.append("posting_date >= %(from_date)s")
    if to_date:
        conditions.append("posting_date <= %(to_date)s")
    
    entries = frappe.db.sql("""
        SELECT 
            name,
            sales_invoice,
            posting_date,
            commission_amount,
            currency
        FROM `tabAgent Commission Entry`
        WHERE {0}
        ORDER BY posting_date
    """.format(" AND ".join(conditions)), {
        "agent": agent,
        "from_date": from_date,
        "to_date": to_date
    }, as_dict=1)
    
    return entries