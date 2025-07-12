# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate, today


class AgentCommissionEntry(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		agent: DF.Link
		amended_from: DF.Link | None
		calculation_details: DF.TextEditor | None
		commission_items: DF.Table
		commission_payment_voucher: DF.Link | None
		company: DF.Link
		currency: DF.Link | None
		customer: DF.Link | None
		exchange_rate: DF.Float | None
		naming_series: DF.Literal["ACE-.YYYY.-"]
		outstanding_amount: DF.Currency | None
		paid_amount: DF.Currency | None
		payment_date: DF.Date | None
		payment_status: DF.Literal["Pending", "Partially Paid", "Paid", "Cancelled"]
		posting_date: DF.Date | None
		remarks: DF.TextEditor | None
		sales_invoice: DF.Link
		total_commission_amount: DF.Currency
	# end: auto-generated types

	def validate(self):
		self.calculate_totals()
		self.validate_payment_status()

	def calculate_totals(self):
		"""Calculate total commission amount from items"""
		total = 0
		for item in self.commission_items:
			total += flt(item.commission_amount)
		
		self.total_commission_amount = total
		self.calculate_outstanding_amount()

	def calculate_outstanding_amount(self):
		"""Calculate outstanding amount based on payment status"""
		if self.payment_status == "Paid":
			self.paid_amount = self.total_commission_amount
			self.outstanding_amount = 0
		elif self.payment_status == "Partially Paid":
			self.outstanding_amount = flt(self.total_commission_amount) - flt(self.paid_amount or 0)
		else:
			self.paid_amount = 0
			self.outstanding_amount = self.total_commission_amount

	def validate_payment_status(self):
		"""Validate payment status and amounts"""
		if self.payment_status == "Paid" and flt(self.paid_amount or 0) != flt(self.total_commission_amount):
			frappe.throw(_("Paid amount must equal total commission amount when status is 'Paid'"))
		
		if self.payment_status == "Partially Paid" and flt(self.paid_amount or 0) >= flt(self.total_commission_amount):
			frappe.throw(_("Paid amount cannot be greater than or equal to total commission amount when status is 'Partially Paid'"))

	def on_submit(self):
		"""Update payment status when submitted"""
		if not self.payment_status:
			self.payment_status = "Pending"
		self.calculate_outstanding_amount()

	def on_cancel(self):
		"""Handle cancellation"""
		if self.commission_payment_voucher:
			frappe.throw(_("Cannot cancel commission entry that is linked to a payment voucher"))

@frappe.whitelist()
def create_commission_entries(sales_invoice, method=None):
	"""Create commission entries when Sales Invoice is submitted"""
	if not sales_invoice:
		return
	
	# Get commission assignments for this invoice
	customer_assignments = get_customer_assignments(sales_invoice.customer, sales_invoice.company)
	
	if not customer_assignments:
		return
	
	# Get invoice items grouped by item group
	invoice_items = get_invoice_items_by_item_group(sales_invoice.name)
	
	for assignment in customer_assignments:
		create_commission_entry_for_assignment(sales_invoice, assignment, invoice_items)

def create_commission_entry_for_assignment(sales_invoice, assignment, invoice_items):
	"""Create commission entry for a specific agent assignment"""
	commission_items = []
	total_commission = 0
	calculation_details = []
	
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
				commission_amount = calculate_commission_amount(item, commission_rule, assignment)
				
				if commission_amount > 0:
					commission_items.append({
						"item_code": item.item_code,
						"item_name": item.item_name,
						"item_group": item.item_group,
						"qty": item.qty,
						"base_amount": item.base_amount,
						"commission_rate": commission_rule.commission_percentage,
						"commission_amount": commission_amount
					})
					
					total_commission += commission_amount
					calculation_details.append(
						f"Item: {item.item_name} - Amount: {item.base_amount} × Rate: {commission_rule.commission_percentage}% = {commission_amount}"
					)
	
	if commission_items:
		entry = frappe.new_doc("Agent Commission Entry")
		entry.agent = assignment.agent
		entry.sales_invoice = sales_invoice.name
		entry.calculation_details = "\n".join(calculation_details)
		
		for item in commission_items:
			entry.append("commission_items", item)
		
		entry.insert()
		entry.submit()

def calculate_commission_amount(item, commission_rule, assignment):
	"""Calculate commission amount based on rule and assignment"""
	base_amount = flt(item.base_amount)
	commission_rate = flt(commission_rule.commission_percentage)
	
	# Check for override in assignment
	if assignment.get("commission_override") and assignment.get("override_commission_percentage"):
		commission_rate = flt(assignment.override_commission_percentage)
	
	commission_amount = base_amount * commission_rate / 100
	
	# Apply minimum and maximum limits
	if commission_rule.minimum_commission_amount and commission_amount < flt(commission_rule.minimum_commission_amount):
		commission_amount = flt(commission_rule.minimum_commission_amount)
	elif commission_rule.maximum_commission_amount and commission_amount > flt(commission_rule.maximum_commission_amount):
		commission_amount = flt(commission_rule.maximum_commission_amount)
	
	return commission_amount

def get_customer_assignments(customer, company):
	"""Get active agent assignments for customer"""
	return frappe.get_all("Agent Customer Assignment",
		filters={
			"customer": customer,
			"company": company,
			"status": "Active",
			"assignment_date": ("<=", frappe.utils.today())
		},
		fields=["agent", "priority", "exclusive_assignment", "commission_override", "override_commission_percentage"],
		order_by="priority"
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
	commission_rules = frappe.get_all("Agent Commission Rule",
		filters={
			"agent": agent,
			"company": company,
			"status": "Active",
			"effective_from": ("<=", posting_date),
			"effective_to": [">=", posting_date, "is", "set"]
		},
		fields=["name", "commission_percentage", "minimum_commission_amount", "maximum_commission_amount"],
		order_by="effective_from desc"
	)
	
	for rule in commission_rules:
		# Check if item group is in commission rates
		rates = frappe.get_all("Agent Commission Rate",
			filters={"parent": rule.name, "item_group": item_group},
			fields=["commission_percentage"]
		)
		if rates:
			rule.commission_percentage = rates[0].commission_percentage
			return rule
	
	return None

@frappe.whitelist()
def cancel_commission_entries(sales_invoice, method=None):
	"""Cancel commission entries when Sales Invoice is cancelled"""
	if not sales_invoice:
		return
	
	commission_entries = frappe.get_all("Agent Commission Entry",
		filters={"sales_invoice": sales_invoice.name},
		fields=["name"]
	)
	
	for entry in commission_entries:
		doc = frappe.get_doc("Agent Commission Entry", entry.name)
		if doc.docstatus == 1:
			doc.cancel()

@frappe.whitelist()
def update_commission_payment_status(payment_entry, method=None):
	"""Update commission payment status when Payment Entry is submitted"""
	if not payment_entry:
		return
	
	# Get commission entries for invoices in this payment
	invoices = frappe.get_all("Payment Entry Reference",
		filters={"parent": payment_entry.name, "reference_doctype": "Sales Invoice"},
		fields=["reference_name"]
	)
	
	for invoice in invoices:
		commission_entries = frappe.get_all("Agent Commission Entry",
			filters={"sales_invoice": invoice.reference_name},
			fields=["name"]
		)
		
		for entry in commission_entries:
			doc = frappe.get_doc("Agent Commission Entry", entry.name)
			doc.payment_status = "Paid"
			doc.payment_date = payment_entry.posting_date
			doc.save()

@frappe.whitelist()
def revert_commission_payment_status(payment_entry, method=None):
	"""Revert commission payment status when Payment Entry is cancelled"""
	if not payment_entry:
		return
	
	# Get commission entries for invoices in this payment
	invoices = frappe.get_all("Payment Entry Reference",
		filters={"parent": payment_entry.name, "reference_doctype": "Sales Invoice"},
		fields=["reference_name"]
	)
	
	for invoice in invoices:
		commission_entries = frappe.get_all("Agent Commission Entry",
			filters={"sales_invoice": invoice.reference_name},
			fields=["name"]
		)
		
		for entry in commission_entries:
			doc = frappe.get_doc("Agent Commission Entry", entry.name)
			doc.payment_status = "Pending"
			doc.payment_date = None
			doc.save()