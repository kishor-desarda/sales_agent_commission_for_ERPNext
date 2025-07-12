# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, today


class AgentCommissionRule(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		agent: DF.Link
		amended_from: DF.Link | None
		calculation_method: DF.Literal["Percentage", "Fixed Amount", "Tiered"]
		commission_rates: DF.Table
		company: DF.Link
		effective_from: DF.Date
		effective_to: DF.Date | None
		maximum_commission_amount: DF.Currency | None
		minimum_commission_amount: DF.Currency | None
		notes: DF.TextEditor | None
		status: DF.Literal["Active", "Inactive"]
	# end: auto-generated types

	def validate(self):
		self.validate_dates()
		self.validate_commission_rates()
		self.validate_calculation_method()

	def validate_dates(self):
		"""Validate effective dates"""
		if self.effective_to and self.effective_from > self.effective_to:
			frappe.throw(_("Effective from date cannot be after effective to date"))
		
		# Check for overlapping rules
		self.check_overlapping_rules()

	def validate_commission_rates(self):
		"""Validate commission rates"""
		if not self.commission_rates:
			frappe.throw(_("At least one commission rate must be defined"))
		
		item_groups = []
		for rate in self.commission_rates:
			if not rate.item_group:
				frappe.throw(_("Item group is required for all commission rates"))
			
			if rate.item_group in item_groups:
				frappe.throw(_("Duplicate item group: {0}").format(rate.item_group))
			
			item_groups.append(rate.item_group)
			
			# Validate based on calculation method
			if self.calculation_method == "Percentage":
				if not rate.commission_percentage:
					frappe.throw(_("Commission percentage is required for item group: {0}").format(rate.item_group))
				if rate.commission_percentage < 0 or rate.commission_percentage > 100:
					frappe.throw(_("Commission percentage must be between 0 and 100 for item group: {0}").format(rate.item_group))
			
			elif self.calculation_method == "Fixed Amount":
				if not rate.fixed_amount:
					frappe.throw(_("Fixed amount is required for item group: {0}").format(rate.item_group))
				if rate.fixed_amount < 0:
					frappe.throw(_("Fixed amount cannot be negative for item group: {0}").format(rate.item_group))

	def validate_calculation_method(self):
		"""Validate calculation method settings"""
		if self.calculation_method == "Tiered":
			# Validate tiered rates for each commission rate
			for rate in self.commission_rates:
				if not rate.tiered_rates:
					frappe.throw(_("Tiered rates are required for item group: {0}").format(rate.item_group))
				
				# Validate tiered rates
				from_amounts = []
				for tier in rate.tiered_rates:
					if tier.from_amount in from_amounts:
						frappe.throw(_("Duplicate from amount in tiered rates for item group: {0}").format(rate.item_group))
					
					from_amounts.append(tier.from_amount)
					
					if tier.from_amount < 0:
						frappe.throw(_("From amount cannot be negative in tiered rates"))
					
					if tier.to_amount and tier.from_amount >= tier.to_amount:
						frappe.throw(_("From amount must be less than to amount in tiered rates"))
					
					if not tier.commission_percentage:
						frappe.throw(_("Commission percentage is required in tiered rates"))
					
					if tier.commission_percentage < 0 or tier.commission_percentage > 100:
						frappe.throw(_("Commission percentage must be between 0 and 100 in tiered rates"))

	def check_overlapping_rules(self):
		"""Check for overlapping commission rules"""
		conditions = [
			"agent = %(agent)s",
			"company = %(company)s",
			"status = 'Active'",
			"name != %(name)s"
		]
		
		if self.effective_to:
			conditions.extend([
				"(effective_from <= %(effective_to)s AND (effective_to IS NULL OR effective_to >= %(effective_from)s))"
			])
		else:
			conditions.extend([
				"(effective_to IS NULL OR effective_to >= %(effective_from)s)"
			])
		
		overlapping = frappe.db.sql("""
			SELECT name, effective_from, effective_to
			FROM `tabAgent Commission Rule`
			WHERE {}
		""".format(" AND ".join(conditions)), {
			"agent": self.agent,
			"company": self.company,
			"name": self.name,
			"effective_from": self.effective_from,
			"effective_to": self.effective_to
		}, as_dict=1)
		
		if overlapping:
			frappe.throw(_("Commission rule overlaps with existing rule: {0}").format(
				overlapping[0].name
			))

	def on_submit(self):
		"""Handle submission"""
		if not self.status:
			self.status = "Active"

	def on_cancel(self):
		"""Handle cancellation"""
		# Check if there are commission entries using this rule
		commission_entries = frappe.get_all("Agent Commission Entry",
			filters={"agent": self.agent},
			fields=["name"]
		)
		
		if commission_entries:
			frappe.throw(_("Cannot cancel rule with existing commission entries"))

@frappe.whitelist()
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
		fields=["name", "calculation_method", "minimum_commission_amount", "maximum_commission_amount"],
		order_by="effective_from desc"
	)
	
	for rule in commission_rules:
		# Check if item group is in commission rates
		rates = frappe.get_all("Agent Commission Rate",
			filters={"parent": rule.name, "item_group": item_group},
			fields=["commission_percentage", "fixed_amount"]
		)
		if rates:
			rate = rates[0]
			rule.commission_percentage = rate.commission_percentage
			rule.fixed_amount = rate.fixed_amount
			return rule
	
	return None