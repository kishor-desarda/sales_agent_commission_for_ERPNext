# -*- coding: utf-8 -*-
# Copyright (c) 2024, Sales Agent Commission and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt, getdate, nowdate
from frappe import _

class AgentCommissionEntry(Document):
    def validate(self):
        self.calculate_commission_amount()
        self.set_status()
        
    def calculate_commission_amount(self):
        """Calculate commission based on ex-works value"""
        self.ex_works_value = flt(self.invoice_amount) - flt(self.freight_charges) - flt(self.logistics_charges)
        self.commission_amount = flt(self.ex_works_value) * flt(self.commission_rate) / 100
        
    def set_status(self):
        """Set status based on payment"""
        if self.is_paid:
            self.status = "Paid"
        elif self.is_invoice_paid:
            self.status = "Due"
        else:
            self.status = "Pending"
    
    def on_submit(self):
        """Create ledger entry on submission"""
        self.create_ledger_entry()
        
    def create_ledger_entry(self):
        """Create entry in Agent Ledger"""
        ledger_entry = frappe.get_doc({
            "doctype": "Agent Ledger Entry",
            "agent": self.agent,
            "posting_date": self.posting_date,
            "entry_type": "Commission",
            "reference_type": "Agent Commission Entry",
            "reference_name": self.name,
            "sales_invoice": self.sales_invoice,
            "debit": self.commission_amount,
            "credit": 0,
            "balance": self.get_running_balance() + self.commission_amount,
            "remarks": f"Commission for Invoice {self.sales_invoice}"
        })
        ledger_entry.insert()
        
    def get_running_balance(self):
        """Get running balance for agent"""
        last_entry = frappe.db.sql("""
            SELECT balance 
            FROM `tabAgent Ledger Entry` 
            WHERE agent = %s 
            ORDER BY creation DESC 
            LIMIT 1
        """, self.agent)
        
        return flt(last_entry[0][0]) if last_entry else 0
    
    def on_cancel(self):
        """Cancel related ledger entries"""
        frappe.db.sql("""
            UPDATE `tabAgent Ledger Entry`
            SET docstatus = 2
            WHERE reference_type = 'Agent Commission Entry'
            AND reference_name = %s
        """, self.name)

@frappe.whitelist()
def create_commission_from_invoice(sales_invoice):
    """Create commission entry from Sales Invoice"""
    invoice = frappe.get_doc("Sales Invoice", sales_invoice)
    
    # Get applicable agents
    agents = get_applicable_agents(invoice)
    
    commission_entries = []
    for agent in agents:
        # Calculate commission for each item group
        commission_details = calculate_commission_details(invoice, agent)
        
        if commission_details:
            commission_entry = frappe.get_doc({
                "doctype": "Agent Commission Entry",
                "agent": agent,
                "sales_invoice": sales_invoice,
                "customer": invoice.customer,
                "territory": invoice.territory,
                "posting_date": invoice.posting_date,
                "invoice_amount": invoice.grand_total,
                "freight_charges": get_freight_charges(invoice),
                "logistics_charges": get_logistics_charges(invoice),
                "currency": invoice.currency,
                "commission_details": commission_details
            })
            commission_entry.insert()
            commission_entry.submit()
            commission_entries.append(commission_entry.name)
    
    return commission_entries

def get_applicable_agents(invoice):
    """Get agents applicable for the invoice based on territory/customer"""
    agents = []
    
    # Check customer-specific agents
    customer_agents = frappe.db.sql("""
        SELECT DISTINCT am.name
        FROM `tabAgent Master` am
        INNER JOIN `tabAgent Customer Assignment` aca ON aca.parent = am.name
        WHERE aca.customer = %s
        AND am.status = 'Active'
        AND am.docstatus = 1
    """, invoice.customer, as_dict=1)
    
    # Check territory-specific agents
    if invoice.territory:
        territory_agents = frappe.db.sql("""
            SELECT DISTINCT am.name
            FROM `tabAgent Master` am
            INNER JOIN `tabAgent Territory Assignment` ata ON ata.parent = am.name
            WHERE ata.territory = %s
            AND am.status = 'Active'
            AND am.docstatus = 1
        """, invoice.territory, as_dict=1)
        
        agents.extend([a.name for a in territory_agents])
    
    agents.extend([a.name for a in customer_agents])
    return list(set(agents))  # Remove duplicates

def calculate_commission_details(invoice, agent):
    """Calculate commission details for each item group"""
    from sales_agent_commission.doctype.agent_master.agent_master import get_agent_commission_rate
    
    item_group_totals = {}
    
    # Group items by item group
    for item in invoice.items:
        item_group = frappe.db.get_value("Item", item.item_code, "item_group")
        if item_group not in item_group_totals:
            item_group_totals[item_group] = 0
        item_group_totals[item_group] += item.amount
    
    # Calculate commission for each item group
    commission_details = []
    for item_group, amount in item_group_totals.items():
        rate = get_agent_commission_rate(agent, item_group, invoice.customer, invoice.territory)
        if rate > 0:
            commission_details.append({
                "item_group": item_group,
                "amount": amount,
                "commission_rate": rate,
                "commission_amount": flt(amount * rate / 100)
            })
    
    return commission_details

def get_freight_charges(invoice):
    """Extract freight charges from invoice"""
    freight = 0
    for tax in invoice.taxes:
        if "freight" in tax.description.lower() or "shipping" in tax.description.lower():
            freight += tax.tax_amount
    return freight

def get_logistics_charges(invoice):
    """Extract logistics charges from invoice"""
    logistics = 0
    for tax in invoice.taxes:
        if "logistics" in tax.description.lower() or "handling" in tax.description.lower():
            logistics += tax.tax_amount
    return logistics

@frappe.whitelist()
def update_payment_status(sales_invoice):
    """Update commission entries when invoice is paid"""
    frappe.db.sql("""
        UPDATE `tabAgent Commission Entry`
        SET is_invoice_paid = 1, status = 'Due'
        WHERE sales_invoice = %s
        AND docstatus = 1
    """, sales_invoice)
    
    frappe.db.commit()