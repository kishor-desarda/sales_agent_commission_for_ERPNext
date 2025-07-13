# -*- coding: utf-8 -*-
# Copyright (c) 2024, Sales Agent Commission and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import getdate, nowdate, flt
from frappe import _

class AgentMaster(Document):
    def validate(self):
        self.validate_commission_rates()
        self.validate_territories_and_customers()
        self.validate_bank_accounts()
        self.set_agent_code()
        
    def validate_commission_rates(self):
        """Validate commission rates don't exceed 100%"""
        for rate in self.commission_rates:
            if flt(rate.commission_percent) > 100:
                frappe.throw(_("Commission percentage cannot exceed 100% for Item Group {0}").format(rate.item_group))
            if flt(rate.commission_percent) < 0:
                frappe.throw(_("Commission percentage cannot be negative for Item Group {0}").format(rate.item_group))
    
    def validate_territories_and_customers(self):
        """Ensure either territory or customer is specified"""
        if not self.territories and not self.customer_assignments:
            frappe.throw(_("Please assign at least one Territory or Customer to the Agent"))
    
    def validate_bank_accounts(self):
        """Ensure at least one bank account is primary"""
        primary_count = sum(1 for acc in self.bank_accounts if acc.is_primary)
        if self.bank_accounts and primary_count == 0:
            frappe.throw(_("Please mark at least one bank account as primary"))
        elif primary_count > 1:
            frappe.throw(_("Only one bank account can be marked as primary"))
    
    def set_agent_code(self):
        """Auto-generate agent code if not provided"""
        if not self.agent_code:
            self.agent_code = self.generate_agent_code()
    
    def generate_agent_code(self):
        """Generate unique agent code"""
        prefix = "AG-"
        count = frappe.db.count("Agent Master") + 1
        return f"{prefix}{str(count).zfill(5)}"
    
    def on_submit(self):
        """Create ledger account for agent"""
        self.create_agent_ledger_account()
        frappe.msgprint(_("Agent {0} onboarded successfully").format(self.agent_name))
    
    def create_agent_ledger_account(self):
        """Create a ledger account for commission tracking"""
        if not frappe.db.exists("Account", {"account_name": self.agent_name, "account_type": "Payable"}):
            company = frappe.db.get_single_value("Global Defaults", "default_company")
            parent_account = frappe.db.get_value("Account", 
                {"account_type": "Payable", "is_group": 1, "company": company}, 
                "name")
            
            if parent_account:
                account = frappe.get_doc({
                    "doctype": "Account",
                    "account_name": self.agent_name,
                    "parent_account": parent_account,
                    "account_type": "Payable",
                    "company": company,
                    "account_currency": self.currency or frappe.db.get_value("Company", company, "default_currency")
                })
                account.insert()
                self.db_set("ledger_account", account.name)

@frappe.whitelist()
def get_agent_commission_rate(agent, item_group, customer=None, territory=None):
    """Get applicable commission rate for agent"""
    agent_doc = frappe.get_doc("Agent Master", agent)
    
    # Check customer-specific rates first
    if customer:
        for assignment in agent_doc.customer_assignments:
            if assignment.customer == customer:
                for rate in agent_doc.commission_rates:
                    if rate.item_group == item_group and rate.applicable_for == "Customer" and rate.customer == customer:
                        return flt(rate.commission_percent)
    
    # Check territory-specific rates
    if territory:
        for terr in agent_doc.territories:
            if terr.territory == territory:
                for rate in agent_doc.commission_rates:
                    if rate.item_group == item_group and rate.applicable_for == "Territory" and rate.territory == territory:
                        return flt(rate.commission_percent)
    
    # Return default rate for item group
    for rate in agent_doc.commission_rates:
        if rate.item_group == item_group and rate.applicable_for == "All":
            return flt(rate.commission_percent)
    
    return 0