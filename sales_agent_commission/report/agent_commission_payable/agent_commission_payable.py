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
			"fieldname": "total_commission",
			"label": _("Total Commission"),
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
			"fieldname": "pending_entries",
			"label": _("Pending Entries"),
			"fieldtype": "Int",
			"width": 100
		},
		{
			"fieldname": "last_payment_date",
			"label": _("Last Payment Date"),
			"fieldtype": "Date",
			"width": 120
		}
	]
	
	return columns

def get_data(filters):
	conditions = get_conditions(filters)
	
	data = frappe.db.sql("""
		SELECT 
			ace.agent,
			sp.partner_name as agent_name,
			SUM(ace.total_commission_amount) as total_commission,
			SUM(ace.paid_amount) as paid_amount,
			SUM(ace.outstanding_amount) as outstanding_amount,
			COUNT(CASE WHEN ace.payment_status IN ('Pending', 'Partially Paid') THEN 1 END) as pending_entries,
			MAX(ace.payment_date) as last_payment_date
		FROM `tabAgent Commission Entry` ace
		LEFT JOIN `tabSales Partner` sp ON ace.agent = sp.name
		WHERE ace.docstatus = 1
		{conditions}
		GROUP BY ace.agent
		HAVING outstanding_amount > 0
		ORDER BY outstanding_amount DESC
	""".format(conditions=conditions), filters, as_dict=1)
	
	return data

def get_conditions(filters):
	conditions = ""
	
	if filters.get("agent"):
		conditions += " AND ace.agent = %(agent)s"
	
	if filters.get("company"):
		conditions += " AND ace.company = %(company)s"
	
	if filters.get("from_date"):
		conditions += " AND ace.posting_date >= %(from_date)s"
	
	if filters.get("to_date"):
		conditions += " AND ace.posting_date <= %(to_date)s"
	
	return conditions

def get_chart_data(filters, data):
	if not data:
		return None
	
	# Prepare chart data
	labels = [row.get("agent_name") or row.get("agent") for row in data]
	datasets = [
		{
			"name": "Outstanding Amount",
			"values": [row.get("outstanding_amount", 0) for row in data]
		}
	]
	
	return {
		"data": {
			"labels": labels,
			"datasets": datasets
		},
		"type": "bar",
		"colors": ["#ff6b6b"],
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
		}
	]