# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, today


class SalesAgentCustomerAssignment(Document):
	def validate(self):
		"""Validate customer assignment"""
		self.validate_dates()
		self.validate_exclusive_assignment()
		self.validate_agent_status()

	def validate_dates(self):
		"""Validate validity dates"""
		if self.valid_to and getdate(self.valid_from) > getdate(self.valid_to):
			frappe.throw(_("Valid From date cannot be after Valid To date"))

	def validate_exclusive_assignment(self):
		"""Validate exclusive assignment"""
		if self.is_exclusive:
			# Check if customer is already exclusively assigned to another agent
			existing_assignment = frappe.get_all("Sales Agent Customer Assignment",
				filters={
					"customer": self.customer,
					"is_exclusive": 1,
					"status": "Active",
					"name": ["!=", self.name],
					"valid_from": ["<=", today()],
					"valid_to": [">=", today()]
				},
				fields=["name", "sales_agent"]
			)
			
			if existing_assignment:
				frappe.throw(_("Customer {0} is already exclusively assigned to Sales Agent {1}").format(
					self.customer, existing_assignment[0].sales_agent
				))

	def validate_agent_status(self):
		"""Validate sales agent status"""
		agent_status = frappe.get_value("Sales Agent", self.sales_agent, "status")
		if agent_status != "Active":
			frappe.throw(_("Sales Agent {0} is not active").format(self.sales_agent))

	def on_submit(self):
		"""Handle submission"""
		self.update_customer_primary_agent()

	def update_customer_primary_agent(self):
		"""Update customer's primary sales agent"""
		# Update customer's primary sales agent if this is the first assignment
		customer_doc = frappe.get_doc("Customer", self.customer)
		if not customer_doc.primary_sales_agent:
			customer_doc.primary_sales_agent = self.sales_agent
			customer_doc.save()

	def on_cancel(self):
		"""Handle cancellation"""
		self.clear_customer_primary_agent()

	def clear_customer_primary_agent(self):
		"""Clear customer's primary sales agent if this was the primary assignment"""
		customer_doc = frappe.get_doc("Customer", self.customer)
		if customer_doc.primary_sales_agent == self.sales_agent:
			# Find another active assignment
			other_assignment = frappe.get_all("Sales Agent Customer Assignment",
				filters={
					"customer": self.customer,
					"status": "Active",
					"name": ["!=", self.name],
					"docstatus": 1
				},
				fields=["sales_agent"],
				limit=1
			)
			
			if other_assignment:
				customer_doc.primary_sales_agent = other_assignment[0].sales_agent
			else:
				customer_doc.primary_sales_agent = None
			
			customer_doc.save()


@frappe.whitelist()
def get_assigned_customers(sales_agent):
	"""Get customers assigned to a sales agent"""
	return frappe.get_all("Sales Agent Customer Assignment",
		filters={
			"sales_agent": sales_agent,
			"status": "Active",
			"docstatus": 1,
			"valid_from": ["<=", today()],
			"valid_to": [">=", today()]
		},
		fields=["customer", "territory", "assignment_date", "is_exclusive", "priority"]
	)

@frappe.whitelist()
def get_agent_for_customer(customer):
	"""Get sales agent for a customer"""
	assignment = frappe.get_all("Sales Agent Customer Assignment",
		filters={
			"customer": customer,
			"status": "Active",
			"docstatus": 1,
			"valid_from": ["<=", today()],
			"valid_to": [">=", today()]
		},
		fields=["sales_agent", "is_exclusive", "priority"],
		order_by="is_exclusive desc, priority desc, assignment_date desc",
		limit=1
	)
	
	return assignment[0] if assignment else None