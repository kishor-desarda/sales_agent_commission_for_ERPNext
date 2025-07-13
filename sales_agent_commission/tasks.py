# -*- coding: utf-8 -*-
# Copyright (c) 2024, Sales Agent Commission and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import today, add_days, getdate, get_datetime, now_datetime
from datetime import datetime, timedelta

def check_agreement_expiry():
    """Daily task to check and update agent agreement expiry status"""
    # Get all active agents with expiring agreements
    agents = frappe.db.sql("""
        SELECT name, agent_name, agreement_expiry_date, email
        FROM `tabAgent Master`
        WHERE status = 'Active'
        AND agreement_expiry_date IS NOT NULL
        AND docstatus = 1
    """, as_dict=1)
    
    today_date = getdate(today())
    notification_days = [30, 15, 7, 1]  # Days before expiry to send notifications
    
    for agent in agents:
        expiry_date = getdate(agent.agreement_expiry_date)
        days_to_expiry = (expiry_date - today_date).days
        
        # Update agreement status if expired
        if days_to_expiry < 0:
            frappe.db.set_value("Agent Master", agent.name, "agreement_status", "Expired")
            frappe.db.set_value("Agent Master", agent.name, "status", "Inactive")
            
            # Send expiry notification
            send_agreement_expiry_notification(agent, "expired")
            
        # Send reminder notifications
        elif days_to_expiry in notification_days:
            send_agreement_expiry_notification(agent, "expiring", days_to_expiry)

def send_agreement_expiry_notification(agent, status, days_to_expiry=None):
    """Send email notification for agreement expiry"""
    if status == "expired":
        subject = f"Agent Agreement Expired - {agent.agent_name}"
        message = f"""
        <p>Dear Team,</p>
        <p>The agreement for agent <b>{agent.agent_name}</b> has expired on {agent.agreement_expiry_date}.</p>
        <p>The agent status has been automatically set to Inactive.</p>
        <p>Please renew the agreement to continue commission calculations.</p>
        """
    else:
        subject = f"Agent Agreement Expiring in {days_to_expiry} days - {agent.agent_name}"
        message = f"""
        <p>Dear Team,</p>
        <p>The agreement for agent <b>{agent.agent_name}</b> will expire on {agent.agreement_expiry_date}.</p>
        <p>Please take necessary action to renew the agreement.</p>
        """
    
    # Send to agent email and system admins
    recipients = [agent.email] if agent.email else []
    recipients.extend(frappe.db.sql_list("""
        SELECT email FROM `tabUser` 
        WHERE enabled = 1 AND name IN (
            SELECT parent FROM `tabHas Role` 
            WHERE role = 'Sales Manager'
        )
    """))
    
    if recipients:
        frappe.sendmail(
            recipients=recipients,
            subject=subject,
            message=message
        )

def update_commission_status_daily():
    """Daily task to update commission status based on payment reconciliation"""
    # Get all pending commission entries where invoice is paid
    entries = frappe.db.sql("""
        SELECT ce.name, ce.sales_invoice
        FROM `tabAgent Commission Entry` ce
        INNER JOIN `tabSales Invoice` si ON ce.sales_invoice = si.name
        WHERE ce.status = 'Pending'
        AND ce.docstatus = 1
        AND si.outstanding_amount = 0
    """, as_dict=1)
    
    for entry in entries:
        # Update to Due status
        frappe.db.set_value("Agent Commission Entry", entry.name, {
            "is_invoice_paid": 1,
            "status": "Due",
            "invoice_payment_date": today()
        })
    
    if entries:
        frappe.db.commit()
        print(f"Updated {len(entries)} commission entries to Due status")

def send_commission_statements():
    """Weekly task to send commission statements to agents"""
    # Get all active agents
    agents = frappe.get_all("Agent Master", 
        filters={"status": "Active", "docstatus": 1},
        fields=["name", "agent_name", "email"])
    
    for agent in agents:
        if not agent.email:
            continue
            
        # Get commission summary for the week
        from_date = add_days(today(), -7)
        to_date = today()
        
        summary = get_agent_commission_summary(agent.name, from_date, to_date)
        
        if summary['total_entries'] > 0:
            send_commission_statement_email(agent, summary, from_date, to_date)

def get_agent_commission_summary(agent, from_date, to_date):
    """Get commission summary for an agent"""
    summary = frappe.db.sql("""
        SELECT 
            COUNT(*) as total_entries,
            SUM(CASE WHEN status = 'Pending' THEN commission_amount ELSE 0 END) as pending_amount,
            SUM(CASE WHEN status = 'Due' THEN commission_amount ELSE 0 END) as due_amount,
            SUM(CASE WHEN status = 'Paid' THEN commission_amount ELSE 0 END) as paid_amount,
            SUM(commission_amount) as total_amount
        FROM `tabAgent Commission Entry`
        WHERE agent = %s
        AND posting_date BETWEEN %s AND %s
        AND docstatus = 1
    """, (agent, from_date, to_date), as_dict=1)[0]
    
    return summary

def send_commission_statement_email(agent, summary, from_date, to_date):
    """Send commission statement email to agent"""
    subject = f"Weekly Commission Statement - {agent.agent_name}"
    
    message = f"""
    <h3>Commission Statement</h3>
    <p>Dear {agent.agent_name},</p>
    <p>Please find below your commission statement for the period {from_date} to {to_date}:</p>
    
    <table border="1" cellpadding="5" cellspacing="0">
        <tr>
            <th>Description</th>
            <th>Amount</th>
        </tr>
        <tr>
            <td>Total Commission Earned</td>
            <td>{summary.total_amount:,.2f}</td>
        </tr>
        <tr>
            <td>Pending (Invoice not paid)</td>
            <td>{summary.pending_amount:,.2f}</td>
        </tr>
        <tr>
            <td>Due for Payment</td>
            <td>{summary.due_amount:,.2f}</td>
        </tr>
        <tr>
            <td>Already Paid</td>
            <td>{summary.paid_amount:,.2f}</td>
        </tr>
    </table>
    
    <p>For detailed information, please login to the system.</p>
    <p>Thank you for your continued partnership.</p>
    """
    
    frappe.sendmail(
        recipients=[agent.email],
        subject=subject,
        message=message
    )

def generate_monthly_commission_report():
    """Monthly task to generate commission reports"""
    # Get first and last day of previous month
    today_date = getdate(today())
    first_day = today_date.replace(day=1) - timedelta(days=1)
    first_day = first_day.replace(day=1)
    last_day = today_date.replace(day=1) - timedelta(days=1)
    
    # Generate report data
    report_data = frappe.db.sql("""
        SELECT 
            am.agent_name,
            COUNT(DISTINCT ace.sales_invoice) as total_invoices,
            SUM(ace.commission_amount) as total_commission,
            SUM(CASE WHEN ace.status = 'Paid' THEN ace.commission_amount ELSE 0 END) as paid_amount,
            SUM(CASE WHEN ace.status IN ('Pending', 'Due') THEN ace.commission_amount ELSE 0 END) as outstanding_amount
        FROM `tabAgent Commission Entry` ace
        INNER JOIN `tabAgent Master` am ON ace.agent = am.name
        WHERE ace.posting_date BETWEEN %s AND %s
        AND ace.docstatus = 1
        GROUP BY ace.agent
        ORDER BY total_commission DESC
    """, (first_day, last_day), as_dict=1)
    
    if report_data:
        # Create a summary report document or send email
        send_monthly_commission_report(report_data, first_day, last_day)

def send_monthly_commission_report(report_data, from_date, to_date):
    """Send monthly commission report to management"""
    # Get all users with Sales Manager role
    recipients = frappe.db.sql_list("""
        SELECT email FROM `tabUser` 
        WHERE enabled = 1 AND name IN (
            SELECT parent FROM `tabHas Role` 
            WHERE role IN ('Sales Manager', 'Accounts Manager')
        )
    """)
    
    if not recipients:
        return
    
    subject = f"Monthly Commission Report - {from_date.strftime('%B %Y')}"
    
    # Build HTML table
    table_rows = ""
    total_commission = 0
    total_paid = 0
    total_outstanding = 0
    
    for row in report_data:
        table_rows += f"""
        <tr>
            <td>{row.agent_name}</td>
            <td style="text-align: center">{row.total_invoices}</td>
            <td style="text-align: right">{row.total_commission:,.2f}</td>
            <td style="text-align: right">{row.paid_amount:,.2f}</td>
            <td style="text-align: right">{row.outstanding_amount:,.2f}</td>
        </tr>
        """
        total_commission += row.total_commission
        total_paid += row.paid_amount
        total_outstanding += row.outstanding_amount
    
    message = f"""
    <h3>Monthly Commission Report - {from_date.strftime('%B %Y')}</h3>
    <p>Period: {from_date} to {to_date}</p>
    
    <table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse; width: 100%">
        <thead>
            <tr style="background-color: #f0f0f0">
                <th>Agent Name</th>
                <th>Total Invoices</th>
                <th>Total Commission</th>
                <th>Paid Amount</th>
                <th>Outstanding</th>
            </tr>
        </thead>
        <tbody>
            {table_rows}
        </tbody>
        <tfoot>
            <tr style="background-color: #f0f0f0; font-weight: bold">
                <td>Total</td>
                <td style="text-align: center">{len(report_data)}</td>
                <td style="text-align: right">{total_commission:,.2f}</td>
                <td style="text-align: right">{total_paid:,.2f}</td>
                <td style="text-align: right">{total_outstanding:,.2f}</td>
            </tr>
        </tfoot>
    </table>
    
    <p>This is an automated report generated on {now_datetime().strftime('%Y-%m-%d %H:%M:%S')}</p>
    """
    
    frappe.sendmail(
        recipients=recipients,
        subject=subject,
        message=message
    )