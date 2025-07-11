# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate


class AgentCommissionRule(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		agent: DF.Link
		amended_from: DF.Link | None
		calculation_method: DF.Literal["Percentage", "Fixed Amount", "Tiered"]
		commission_percentage: DF.Float
		company: DF.Link
		effective_from: DF.Date
		effective_to: DF.Date | None
		item_group: DF.Link
		maximum_amount: DF.Currency | None
		minimum_amount: DF.Currency | None
		naming_series: DF.Literal["ACR-.YYYY.-"]
		notes: DF.TextEditor | None
		status: DF.Literal["Active", "Inactive"]
	# end: auto-generated types

	def validate(self):
		self.validate_effective_dates()
		self.validate_duplicate_rules()
		self.validate_commission_percentage()

	def validate_effective_dates(self):
		if self.effective_to and getdate(self.effective_from) > getdate(self.effective_to):
			frappe.throw(_("Effective From date cannot be after Effective To date"))

	def validate_duplicate_rules(self):
		filters = {
			"agent": self.agent,
			"item_group": self.item_group,
			"company": self.company,
			"status": "Active",
			"name": ("!=", self.name)
		}

		# Check for overlapping date ranges
		existing_rules = frappe.get_all("Agent Commission Rule", 
			filters=filters,
			fields=["name", "effective_from", "effective_to"]
		)

		for rule in existing_rules:
			if self.is_date_overlap(rule):
				frappe.throw(_("Commission rule for Agent {0} and Item Group {1} already exists for overlapping dates")
					.format(self.agent, self.item_group))

	def is_date_overlap(self, existing_rule):
		"""Check if current rule dates overlap with existing rule"""
		current_from = getdate(self.effective_from)
		current_to = getdate(self.effective_to) if self.effective_to else None
		existing_from = getdate(existing_rule.effective_from)
		existing_to = getdate(existing_rule.effective_to) if existing_rule.effective_to else None

		# If either rule has no end date, consider it as ongoing
		if not current_to or not existing_to:
			return True

		# Check for date overlap
		return (current_from <= existing_to and current_to >= existing_from)

	def validate_commission_percentage(self):
		if self.calculation_method == "Percentage":
			if not self.commission_percentage or self.commission_percentage <= 0:
				frappe.throw(_("Commission Percentage must be greater than 0 for Percentage calculation method"))
			if self.commission_percentage > 100:
				frappe.throw(_("Commission Percentage cannot be greater than 100%"))

@frappe.whitelist()
def get_applicable_commission_rate(agent, item_group, company, posting_date):
	"""Get applicable commission rate for given parameters"""
	filters = {
		"agent": agent,
		"item_group": item_group,
		"company": company,
		"status": "Active",
		"effective_from": ("<=", posting_date)
	}
	
	# Add effective_to filter if not null
	or_filters = [
		["effective_to", ">=", posting_date],
		["effective_to", "is", "not set"]
	]
	
	rules = frappe.get_all("Agent Commission Rule",
		filters=filters,
		or_filters=or_filters,
		fields=["commission_percentage", "calculation_method", "minimum_amount", "maximum_amount"],
		order_by="effective_from desc",
		limit=1
	)
	
	return rules[0] if rules else None