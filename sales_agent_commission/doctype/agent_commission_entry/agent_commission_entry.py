# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class AgentCommissionEntry(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		agent: DF.Link
		amended_from: DF.Link | None
		base_amount: DF.Currency
		calculation_details: DF.TextEditor | None
		commission_amount: DF.Currency
		commission_amount_company_currency: DF.Currency | None
		commission_rate: DF.Float
		commission_voucher: DF.Link | None
		company: DF.Link
		currency: DF.Link | None
		customer: DF.Link | None
		exchange_rate: DF.Float | None
		item_code: DF.Link | None
		item_group: DF.Link
		item_name: DF.Data | None
		naming_series: DF.Literal["ACE-.YYYY.-"]
		payment_date: DF.Date | None
		payment_status: DF.Literal["Pending", "Paid", "Partially Paid", "Cancelled"]
		posting_date: DF.Date | None
		qty: DF.Float | None
		remarks: DF.TextEditor | None
		sales_invoice: DF.Link
	# end: auto-generated types

	def validate(self):
		self.calculate_commission_amount_in_company_currency()

	def calculate_commission_amount_in_company_currency(self):
		if self.commission_amount and self.exchange_rate:
			self.commission_amount_company_currency = flt(self.commission_amount) * flt(self.exchange_rate)

@frappe.whitelist()
def create_commission_entries(sales_invoice, method=None):
	"""Create commission entries when Sales Invoice is submitted"""
	if not sales_invoice:
		return
	
	# Get commission assignments for this invoice
	customer_assignments = get_customer_assignments(sales_invoice.customer, sales_invoice.company)
	
	for assignment in customer_assignments:
		# Get invoice items grouped by item group
		invoice_items = get_invoice_items_by_item_group(sales_invoice.name)
		
		for item_group, items in invoice_items.items():
			# Get applicable commission rate
			commission_rule = get_applicable_commission_rate(
				assignment.agent, 
				item_group, 
				sales_invoice.company, 
				sales_invoice.posting_date
			)
			
			if commission_rule:
				for item in items:
					create_commission_entry(sales_invoice, assignment.agent, item, commission_rule)

def get_customer_assignments(customer, company):
	"""Get active agent assignments for customer"""
	return frappe.get_all("Agent Customer Assignment",
		filters={
			"customer": customer,
			"company": company,
			"status": "Active",
			"assignment_date": ("<=", frappe.utils.today())
		},
		fields=["agent", "priority", "exclusive_assignment"]
	)

def get_invoice_items_by_item_group(sales_invoice):
	"""Get invoice items grouped by item group"""
	items = frappe.get_all("Sales Invoice Item",
		filters={"parent": sales_invoice},
		fields=["item_code", "item_name", "item_group", "qty", "base_amount"]
	)
	
	items_by_group = {}
	for item in items:
		if item.item_group not in items_by_group:
			items_by_group[item.item_group] = []
		items_by_group[item.item_group].append(item)
	
	return items_by_group

def get_applicable_commission_rate(agent, item_group, company, posting_date):
	"""Get applicable commission rate for given parameters"""
	from sales_agent_commission.sales_agent_commission.doctype.agent_commission_rule.agent_commission_rule import get_applicable_commission_rate
	return get_applicable_commission_rate(agent, item_group, company, posting_date)

def create_commission_entry(sales_invoice, agent, item, commission_rule):
	"""Create individual commission entry"""
	commission_amount = flt(item.base_amount) * flt(commission_rule.commission_percentage) / 100
	
	# Apply minimum and maximum limits
	if commission_rule.minimum_amount and commission_amount < flt(commission_rule.minimum_amount):
		commission_amount = flt(commission_rule.minimum_amount)
	elif commission_rule.maximum_amount and commission_amount > flt(commission_rule.maximum_amount):
		commission_amount = flt(commission_rule.maximum_amount)
	
	entry = frappe.new_doc("Agent Commission Entry")
	entry.agent = agent
	entry.sales_invoice = sales_invoice.name
	entry.item_group = item.item_group
	entry.item_code = item.item_code
	entry.item_name = item.item_name
	entry.qty = item.qty
	entry.base_amount = item.base_amount
	entry.commission_rate = commission_rule.commission_percentage
	entry.commission_amount = commission_amount
	entry.calculation_details = f"Base Amount: {item.base_amount} × Rate: {commission_rule.commission_percentage}% = {commission_amount}"
	entry.insert()
	entry.submit()