# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, today


class AgentCustomerAssignment(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		agent: DF.Link
		amended_from: DF.Link | None
		assignment_date: DF.Date
		commission_override: DF.Check
		company: DF.Link
		customer: DF.Link
		end_date: DF.Date | None
		exclusive_assignment: DF.Check
		naming_series: DF.Literal["ACA-.YYYY.-"]
		notes: DF.TextEditor | None
		override_commission_percentage: DF.Float | None
		priority: DF.Int
		status: DF.Literal["Active", "Inactive", "Expired"]
	# end: auto-generated types

	def validate(self):
		self.validate_dates()
		self.validate_exclusive_assignment()
		self.validate_commission_override()

	def validate_dates(self):
		"""Validate assignment dates"""
		if self.end_date and self.assignment_date > self.end_date:
			frappe.throw(_("Assignment date cannot be after end date"))
		
		# Check for overlapping assignments if exclusive
		if self.exclusive_assignment:
			self.check_exclusive_overlap()

	def validate_exclusive_assignment(self):
		"""Validate exclusive assignment"""
		if self.exclusive_assignment:
			# Check if there are other active exclusive assignments
			existing = frappe.get_all("Agent Customer Assignment",
				filters={
					"customer": self.customer,
					"company": self.company,
					"exclusive_assignment": 1,
					"status": "Active",
					"name": ["!=", self.name]
				}
			)
			
			if existing:
				frappe.throw(_("Customer already has an exclusive assignment with another agent"))

	def validate_commission_override(self):
		"""Validate commission override"""
		if self.commission_override and not self.override_commission_percentage:
			frappe.throw(_("Override commission percentage is required when commission override is enabled"))
		
		if self.override_commission_percentage and not self.commission_override:
			frappe.throw(_("Commission override must be enabled to set override percentage"))

	def check_exclusive_overlap(self):
		"""Check for overlapping exclusive assignments"""
		conditions = [
			"customer = %(customer)s",
			"company = %(company)s",
			"exclusive_assignment = 1",
			"status = 'Active'",
			"name != %(name)s"
		]
		
		if self.end_date:
			conditions.extend([
				"(assignment_date <= %(end_date)s AND (end_date IS NULL OR end_date >= %(assignment_date)s))"
			])
		else:
			conditions.extend([
				"(end_date IS NULL OR end_date >= %(assignment_date)s)"
			])
		
		overlapping = frappe.db.sql("""
			SELECT name, agent, assignment_date, end_date
			FROM `tabAgent Customer Assignment`
			WHERE {}
		""".format(" AND ".join(conditions)), {
			"customer": self.customer,
			"company": self.company,
			"name": self.name,
			"assignment_date": self.assignment_date,
			"end_date": self.end_date
		}, as_dict=1)
		
		if overlapping:
			frappe.throw(_("Exclusive assignment overlaps with existing assignment: {0}").format(
				overlapping[0].name
			))

	def on_submit(self):
		"""Handle submission"""
		if not self.status:
			self.status = "Active"

	def on_cancel(self):
		"""Handle cancellation"""
		# Check if there are commission entries linked to this assignment
		commission_entries = frappe.get_all("Agent Commission Entry",
			filters={"agent": self.agent, "customer": self.customer},
			fields=["name"]
		)
		
		if commission_entries:
			frappe.throw(_("Cannot cancel assignment with existing commission entries"))

@frappe.whitelist()
def get_agent_assignments(customer, company, date=None):
	"""Get active agent assignments for a customer"""
	if not date:
		date = today()
	
	return frappe.get_all("Agent Customer Assignment",
		filters={
			"customer": customer,
			"company": company,
			"status": "Active",
			"assignment_date": ("<=", date),
			"end_date": [">=", date, "is", "set"]
		},
		fields=["agent", "priority", "exclusive_assignment", "commission_override", "override_commission_percentage"],
		order_by="priority"
	)