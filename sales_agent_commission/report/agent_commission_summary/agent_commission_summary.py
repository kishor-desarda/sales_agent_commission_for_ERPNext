# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, getdate, today


def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	chart = get_chart_data(filters, data)
	
	return columns, data, None, chart

def get_columns(filters):
	columns = [
		{
			"fieldname": "agent",
			"label": _("Sales Agent"),
			"fieldtype": "Link",
			"options": "Sales Partner",
			"width": 150
		},
		{
			"fieldname": "customer",
			"label": _("Customer"),
			"fieldtype": "Link",
			"options": "Customer",
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
			"fieldname": "total_commission_amount",
			"label": _("Commission Amount"),
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"fieldname": "paid_amount",
			"label": _("Paid Amount"),
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"fieldname": "outstanding_amount",
			"label": _("Outstanding Amount"),
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"fieldname": "payment_status",
			"label": _("Payment Status"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "payment_date",
			"label": _("Payment Date"),
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "commission_payment_voucher",
			"label": _("Payment Voucher"),
			"fieldtype": "Link",
			"options": "Commission Payment Voucher",
			"width": 120
		}
	]
	
	return columns

def get_data(filters):
	conditions = get_conditions(filters)
	
	data = frappe.db.sql("""
		SELECT 
			ace.agent,
			ace.customer,
			ace.sales_invoice,
			ace.posting_date,
			ace.total_commission_amount,
			ace.paid_amount,
			ace.outstanding_amount,
			ace.payment_status,
			ace.payment_date,
			ace.commission_payment_voucher,
			sp.partner_name as agent_name
		FROM `tabAgent Commission Entry` ace
		LEFT JOIN `tabSales Partner` sp ON ace.agent = sp.name
		WHERE ace.docstatus = 1
		{conditions}
		ORDER BY ace.posting_date DESC, ace.agent
	""".format(conditions=conditions), filters, as_dict=1)
	
	return data

def get_conditions(filters):
	conditions = ""
	
	if filters.get("agent"):
		conditions += " AND ace.agent = %(agent)s"
	
	if filters.get("customer"):
		conditions += " AND ace.customer = %(customer)s"
	
	if filters.get("company"):
		conditions += " AND ace.company = %(company)s"
	
	if filters.get("from_date"):
		conditions += " AND ace.posting_date >= %(from_date)s"
	
	if filters.get("to_date"):
		conditions += " AND ace.posting_date <= %(to_date)s"
	
	if filters.get("payment_status"):
		conditions += " AND ace.payment_status = %(payment_status)s"
	
	if filters.get("sales_invoice"):
		conditions += " AND ace.sales_invoice = %(sales_invoice)s"
	
	return conditions

def get_chart_data(filters, data):
	if not data:
		return None
	
	# Group by agent for chart
	agent_data = {}
	for row in data:
		agent = row.get("agent_name") or row.get("agent")
		if agent not in agent_data:
			agent_data[agent] = {
				"total_commission": 0,
				"paid_amount": 0,
				"outstanding_amount": 0
			}
		
		agent_data[agent]["total_commission"] += flt(row.get("total_commission_amount", 0))
		agent_data[agent]["paid_amount"] += flt(row.get("paid_amount", 0))
		agent_data[agent]["outstanding_amount"] += flt(row.get("outstanding_amount", 0))
	
	# Prepare chart data
	labels = list(agent_data.keys())
	datasets = [
		{
			"name": "Total Commission",
			"values": [agent_data[agent]["total_commission"] for agent in labels]
		},
		{
			"name": "Paid Amount",
			"values": [agent_data[agent]["paid_amount"] for agent in labels]
		},
		{
			"name": "Outstanding Amount",
			"values": [agent_data[agent]["outstanding_amount"] for agent in labels]
		}
	]
	
	return {
		"data": {
			"labels": labels,
			"datasets": datasets
		},
		"type": "bar",
		"colors": ["#5e64ff", "#28a745", "#ffc107"],
		"height": 300
	}

def get_filters():
	return [
		{
			"fieldname": "agent",
			"label": _("Sales Agent"),
			"fieldtype": "Link",
			"options": "Sales Partner"
		},
		{
			"fieldname": "customer",
			"label": _("Customer"),
			"fieldtype": "Link",
			"options": "Customer"
		},
		{
			"fieldname": "company",
			"label": _("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company")
		},
		{
			"fieldname": "from_date",
			"label": _("From Date"),
			"fieldtype": "Date",
			"default": getdate(today()).replace(day=1)
		},
		{
			"fieldname": "to_date",
			"label": _("To Date"),
			"fieldtype": "Date",
			"default": today()
		},
		{
			"fieldname": "payment_status",
			"label": _("Payment Status"),
			"fieldtype": "Select",
			"options": "Pending\nPartially Paid\nPaid\nCancelled"
		},
		{
			"fieldname": "sales_invoice",
			"label": _("Sales Invoice"),
			"fieldtype": "Link",
			"options": "Sales Invoice"
		}
	]