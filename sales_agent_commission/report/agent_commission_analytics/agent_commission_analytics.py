# Copyright (c) 2024, Sales Agent Commission and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, getdate

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart_data(data, filters)
    summary = get_report_summary(data)
    
    return columns, data, None, chart, summary

def get_columns():
    return [
        {
            "fieldname": "agent",
            "label": _("Agent Code"),
            "fieldtype": "Link",
            "options": "Agent Master",
            "width": 120
        },
        {
            "fieldname": "agent_name",
            "label": _("Agent Name"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "territory",
            "label": _("Territory"),
            "fieldtype": "Link",
            "options": "Territory",
            "width": 120
        },
        {
            "fieldname": "customer",
            "label": _("Customer"),
            "fieldtype": "Link",
            "options": "Customer",
            "width": 150
        },
        {
            "fieldname": "customer_name",
            "label": _("Customer Name"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "sales_invoice",
            "label": _("Sales Invoice"),
            "fieldtype": "Link",
            "options": "Sales Invoice",
            "width": 120
        },
        {
            "fieldname": "posting_date",
            "label": _("Invoice Date"),
            "fieldtype": "Date",
            "width": 100
        },
        {
            "fieldname": "invoice_amount",
            "label": _("Invoice Amount"),
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "ex_works_value",
            "label": _("Ex-Works Value"),
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "item_group",
            "label": _("Item Group"),
            "fieldtype": "Link",
            "options": "Item Group",
            "width": 120
        },
        {
            "fieldname": "commission_rate",
            "label": _("Commission %"),
            "fieldtype": "Percent",
            "width": 100
        },
        {
            "fieldname": "commission_amount",
            "label": _("Commission Amount"),
            "fieldtype": "Currency",
            "width": 130
        },
        {
            "fieldname": "status",
            "label": _("Status"),
            "fieldtype": "Data",
            "width": 100
        },
        {
            "fieldname": "invoice_payment_date",
            "label": _("Invoice Payment Date"),
            "fieldtype": "Date",
            "width": 130
        },
        {
            "fieldname": "payment_date",
            "label": _("Commission Payment Date"),
            "fieldtype": "Date",
            "width": 150
        },
        {
            "fieldname": "payment_reference",
            "label": _("Payment Reference"),
            "fieldtype": "Link",
            "options": "Agent Commission Payment",
            "width": 130
        }
    ]

def get_data(filters):
    conditions = get_conditions(filters)
    
    query = """
        SELECT 
            ace.agent,
            am.agent_name,
            ace.territory,
            ace.customer,
            c.customer_name,
            ace.sales_invoice,
            ace.posting_date,
            ace.invoice_amount,
            ace.ex_works_value,
            acd.item_group,
            acd.commission_rate,
            acd.commission_amount,
            ace.status,
            ace.invoice_payment_date,
            ace.payment_date,
            ace.payment_reference
        FROM `tabAgent Commission Entry` ace
        INNER JOIN `tabAgent Master` am ON ace.agent = am.name
        LEFT JOIN `tabCustomer` c ON ace.customer = c.name
        LEFT JOIN `tabAgent Commission Detail` acd ON acd.parent = ace.name
        WHERE ace.docstatus = 1
        {conditions}
        ORDER BY ace.posting_date DESC, ace.agent, ace.sales_invoice
    """.format(conditions=conditions)
    
    return frappe.db.sql(query, filters, as_dict=1)

def get_conditions(filters):
    conditions = []
    
    if filters.get("agent"):
        conditions.append("ace.agent = %(agent)s")
    
    if filters.get("from_date"):
        conditions.append("ace.posting_date >= %(from_date)s")
    
    if filters.get("to_date"):
        conditions.append("ace.posting_date <= %(to_date)s")
    
    if filters.get("territory"):
        conditions.append("ace.territory = %(territory)s")
    
    if filters.get("customer"):
        conditions.append("ace.customer = %(customer)s")
    
    if filters.get("item_group"):
        conditions.append("acd.item_group = %(item_group)s")
    
    if filters.get("status"):
        conditions.append("ace.status = %(status)s")
    
    if filters.get("invoice_type"):
        conditions.append("ace.invoice_type = %(invoice_type)s")
    
    return "AND " + " AND ".join(conditions) if conditions else ""

def get_chart_data(data, filters):
    # Commission by Agent
    agent_data = {}
    for row in data:
        if row.agent_name not in agent_data:
            agent_data[row.agent_name] = 0
        agent_data[row.agent_name] += flt(row.commission_amount)
    
    # Commission by Status
    status_data = {
        "Pending": 0,
        "Due": 0,
        "Paid": 0
    }
    for row in data:
        if row.status in status_data:
            status_data[row.status] += flt(row.commission_amount)
    
    chart = {
        "data": {
            "labels": list(agent_data.keys())[:10],  # Top 10 agents
            "datasets": [
                {
                    "name": "Commission Amount",
                    "values": list(agent_data.values())[:10]
                }
            ]
        },
        "type": "bar",
        "colors": ["#7cd6fd"],
        "title": "Top 10 Agents by Commission"
    }
    
    return chart

def get_report_summary(data):
    total_commission = sum(flt(row.commission_amount) for row in data)
    pending_amount = sum(flt(row.commission_amount) for row in data if row.status == "Pending")
    due_amount = sum(flt(row.commission_amount) for row in data if row.status == "Due")
    paid_amount = sum(flt(row.commission_amount) for row in data if row.status == "Paid")
    
    return [
        {
            "value": total_commission,
            "label": _("Total Commission"),
            "datatype": "Currency",
            "color": "blue"
        },
        {
            "value": pending_amount,
            "label": _("Pending Amount"),
            "datatype": "Currency",
            "color": "orange"
        },
        {
            "value": due_amount,
            "label": _("Due Amount"),
            "datatype": "Currency",
            "color": "yellow"
        },
        {
            "value": paid_amount,
            "label": _("Paid Amount"),
            "datatype": "Currency",
            "color": "green"
        }
    ]