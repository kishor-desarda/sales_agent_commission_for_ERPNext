# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class CommissionPaymentVoucher(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from sales_agent_commission.sales_agent_commission.doctype.commission_payment_item.commission_payment_item import CommissionPaymentItem

		agent: DF.Link
		amended_from: DF.Link | None
		commission_entries: DF.Table[CommissionPaymentItem]
		company: DF.Link
		currency: DF.Link
		exchange_rate: DF.Float
		naming_series: DF.Literal["CPV-.YYYY.-"]
		payment_date: DF.Date
		payment_method: DF.Literal["Bank Transfer", "Cash", "Cheque", "Credit Card", "Other"]
		reference_no: DF.Data | None
		remarks: DF.TextEditor | None
		total_commission_amount: DF.Currency
	# end: auto-generated types

	def validate(self):
		self.calculate_totals()
		self.validate_commission_entries()

	def calculate_totals(self):
		"""Calculate total commission amount from entries"""
		total = 0
		for entry in self.commission_entries:
			total += flt(entry.paid_amount)
		
		self.total_commission_amount = total

	def validate_commission_entries(self):
		"""Validate commission entries"""
		if not self.commission_entries:
			frappe.throw(_("Please add at least one commission entry"))
		
		for entry in self.commission_entries:
			if not entry.commission_entry:
				frappe.throw(_("Commission Entry is required for all entries"))
			
			# Validate paid amount
			commission_doc = frappe.get_doc("Agent Commission Entry", entry.commission_entry)
			if flt(entry.paid_amount) > flt(commission_doc.outstanding_amount):
				frappe.throw(_("Paid amount cannot exceed outstanding amount for commission entry {0}").format(entry.commission_entry))

	def on_submit(self):
		"""Update commission entries when voucher is submitted"""
		self.update_commission_entries()

	def on_cancel(self):
		"""Revert commission entries when voucher is cancelled"""
		self.revert_commission_entries()

	def update_commission_entries(self):
		"""Update commission entries with payment information"""
		for entry in self.commission_entries:
			commission_doc = frappe.get_doc("Agent Commission Entry", entry.commission_entry)
			
			# Update paid amount
			commission_doc.paid_amount = flt(commission_doc.paid_amount or 0) + flt(entry.paid_amount)
			commission_doc.commission_payment_voucher = self.name
			commission_doc.payment_date = self.payment_date
			
			# Update payment status
			if flt(commission_doc.paid_amount) >= flt(commission_doc.total_commission_amount):
				commission_doc.payment_status = "Paid"
			else:
				commission_doc.payment_status = "Partially Paid"
			
			commission_doc.calculate_outstanding_amount()
			commission_doc.save()

	def revert_commission_entries(self):
		"""Revert commission entries when voucher is cancelled"""
		for entry in self.commission_entries:
			commission_doc = frappe.get_doc("Agent Commission Entry", entry.commission_entry)
			
			# Revert paid amount
			commission_doc.paid_amount = flt(commission_doc.paid_amount or 0) - flt(entry.paid_amount)
			
			# Clear payment voucher reference
			if commission_doc.commission_payment_voucher == self.name:
				commission_doc.commission_payment_voucher = None
				commission_doc.payment_date = None
			
			# Update payment status
			if flt(commission_doc.paid_amount) <= 0:
				commission_doc.payment_status = "Pending"
			else:
				commission_doc.payment_status = "Partially Paid"
			
			commission_doc.calculate_outstanding_amount()
			commission_doc.save()

@frappe.whitelist()
def get_pending_commission_entries(agent, company):
	"""Get pending commission entries for an agent"""
	return frappe.get_all("Agent Commission Entry",
		filters={
			"agent": agent,
			"company": company,
			"payment_status": ["in", ["Pending", "Partially Paid"]],
			"docstatus": 1
		},
		fields=["name", "sales_invoice", "customer", "posting_date", "total_commission_amount", "paid_amount", "outstanding_amount"]
	)

@frappe.whitelist()
def update_commission_entries(commission_payment_voucher, method=None):
	"""Update commission entries when Commission Payment Voucher is submitted"""
	if not commission_payment_voucher:
		return
	
	doc = frappe.get_doc("Commission Payment Voucher", commission_payment_voucher.name)
	doc.update_commission_entries()

@frappe.whitelist()
def revert_commission_entries(commission_payment_voucher, method=None):
	"""Revert commission entries when Commission Payment Voucher is cancelled"""
	if not commission_payment_voucher:
		return
	
	doc = frappe.get_doc("Commission Payment Voucher", commission_payment_voucher.name)
	doc.revert_commission_entries()