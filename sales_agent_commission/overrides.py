# -*- coding: utf-8 -*-
# Copyright (c) 2024, Sales Agent Commission and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, getdate, nowdate

def create_agent_commission_entries(doc, method):
    """Create commission entries when Sales Invoice is submitted"""
    if doc.docstatus != 1:
        return
        
    # Import the function from the agent commission entry module
    from sales_agent_commission.doctype.agent_commission_entry.agent_commission_entry import create_commission_from_invoice
    
    # Create commission entries
    commission_entries = create_commission_from_invoice(doc.name)
    
    if commission_entries:
        # Update Sales Invoice with commission information
        applicable_agents = frappe.db.sql("""
            SELECT DISTINCT agent_name 
            FROM `tabAgent Commission Entry`
            WHERE sales_invoice = %s
        """, doc.name, as_list=1)
        
        total_commission = frappe.db.sql("""
            SELECT SUM(commission_amount)
            FROM `tabAgent Commission Entry`
            WHERE sales_invoice = %s AND docstatus = 1
        """, doc.name)[0][0] or 0
        
        frappe.db.set_value("Sales Invoice", doc.name, {
            "commission_entries_created": 1,
            "applicable_agents": ", ".join([a[0] for a in applicable_agents]),
            "total_commission_amount": total_commission
        })
        
        frappe.msgprint(_("{0} commission entries created").format(len(commission_entries)))

def cancel_agent_commission_entries(doc, method):
    """Cancel commission entries when Sales Invoice is cancelled"""
    if doc.docstatus != 2:
        return
        
    # Get all commission entries for this invoice
    commission_entries = frappe.get_all("Agent Commission Entry",
        filters={"sales_invoice": doc.name, "docstatus": 1},
        fields=["name"])
    
    for entry in commission_entries:
        commission_doc = frappe.get_doc("Agent Commission Entry", entry.name)
        if commission_doc.is_paid:
            frappe.throw(_("Cannot cancel Sales Invoice. Commission Entry {0} is already paid").format(entry.name))
        commission_doc.cancel()
    
    # Update Sales Invoice
    frappe.db.set_value("Sales Invoice", doc.name, {
        "commission_entries_created": 0,
        "applicable_agents": None,
        "total_commission_amount": 0
    })

def check_invoice_payment_reconciliation(doc, method):
    """Check if payment is against sales invoices with commission"""
    if doc.payment_type != "Receive":
        return
        
    for reference in doc.references:
        if reference.reference_doctype == "Sales Invoice":
            # Check if invoice has commission entries
            has_commission = frappe.db.exists("Agent Commission Entry", {
                "sales_invoice": reference.reference_name,
                "docstatus": 1
            })
            
            if has_commission:
                # Schedule update for commission entries
                frappe.enqueue(
                    update_commission_status_for_invoice,
                    invoice=reference.reference_name,
                    queue='short'
                )

def update_commission_status_for_invoice(invoice):
    """Update commission status when invoice is paid"""
    # Check if invoice is fully paid
    invoice_doc = frappe.get_doc("Sales Invoice", invoice)
    
    if invoice_doc.outstanding_amount == 0:
        # Update commission entries to Due status
        from sales_agent_commission.doctype.agent_commission_entry.agent_commission_entry import update_payment_status
        update_payment_status(invoice)
        
        # Notify agents
        agents = frappe.db.sql("""
            SELECT DISTINCT agent, agent_name
            FROM `tabAgent Commission Entry`
            WHERE sales_invoice = %s AND docstatus = 1
        """, invoice, as_dict=1)
        
        for agent in agents:
            frappe.publish_realtime(
                event='commission_due',
                message={
                    'agent': agent.agent,
                    'agent_name': agent.agent_name,
                    'invoice': invoice
                },
                user=frappe.session.user
            )

def revert_invoice_payment_reconciliation(doc, method):
    """Revert commission status when payment is cancelled"""
    if doc.payment_type != "Receive":
        return
        
    for reference in doc.references:
        if reference.reference_doctype == "Sales Invoice":
            # Revert commission entries to Pending status
            frappe.db.sql("""
                UPDATE `tabAgent Commission Entry`
                SET is_invoice_paid = 0, status = 'Pending'
                WHERE sales_invoice = %s AND docstatus = 1
            """, reference.reference_name)

def update_commission_entries_on_reconciliation(doc, method):
    """Update commission entries when Payment Reconciliation is submitted"""
    # Get all invoices in the reconciliation
    invoices = []
    
    if hasattr(doc, 'invoices'):
        invoices = [d.invoice_number for d in doc.invoices if d.invoice_number]
    elif hasattr(doc, 'allocation'):
        invoices = [d.reference_name for d in doc.allocation if d.reference_type == "Sales Invoice"]
    
    for invoice in invoices:
        # Check if invoice has commission entries
        if frappe.db.exists("Agent Commission Entry", {"sales_invoice": invoice, "docstatus": 1}):
            frappe.enqueue(
                update_commission_status_for_invoice,
                invoice=invoice,
                queue='short'
            )

# Additional utility functions
@frappe.whitelist()
def get_applicable_agents_for_invoice(sales_invoice):
    """Get list of agents applicable for a sales invoice"""
    invoice = frappe.get_doc("Sales Invoice", sales_invoice)
    
    from sales_agent_commission.doctype.agent_commission_entry.agent_commission_entry import get_applicable_agents
    agents = get_applicable_agents(invoice)
    
    agent_details = []
    for agent in agents:
        agent_doc = frappe.get_doc("Agent Master", agent)
        agent_details.append({
            "agent": agent,
            "agent_name": agent_doc.agent_name,
            "status": agent_doc.status
        })
    
    return agent_details

@frappe.whitelist()
def get_commission_summary(agent=None, from_date=None, to_date=None):
    """Get commission summary for dashboard"""
    conditions = ["docstatus = 1"]
    values = {}
    
    if agent:
        conditions.append("agent = %(agent)s")
        values["agent"] = agent
    
    if from_date:
        conditions.append("posting_date >= %(from_date)s")
        values["from_date"] = from_date
        
    if to_date:
        conditions.append("posting_date <= %(to_date)s")
        values["to_date"] = to_date
    
    summary = frappe.db.sql("""
        SELECT 
            COUNT(*) as total_entries,
            SUM(CASE WHEN status = 'Pending' THEN 1 ELSE 0 END) as pending_entries,
            SUM(CASE WHEN status = 'Due' THEN 1 ELSE 0 END) as due_entries,
            SUM(CASE WHEN status = 'Paid' THEN 1 ELSE 0 END) as paid_entries,
            SUM(CASE WHEN status = 'Pending' THEN commission_amount ELSE 0 END) as pending_amount,
            SUM(CASE WHEN status = 'Due' THEN commission_amount ELSE 0 END) as due_amount,
            SUM(CASE WHEN status = 'Paid' THEN commission_amount ELSE 0 END) as paid_amount,
            SUM(commission_amount) as total_amount
        FROM `tabAgent Commission Entry`
        WHERE {0}
    """.format(" AND ".join(conditions)), values, as_dict=1)[0]
    
    return summary