# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate, today, now_datetime


class SalesAgent(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		address_line_1: DF.Data | None
		address_line_2: DF.Data | None
		agent_code: DF.Data
		agent_name: DF.Data
		agent_type: DF.Literal["Internal", "External", "Distributor", "Dealer"]
		amended_from: DF.Link | None
		approval_status: DF.Literal["Draft", "Pending Approval", "Approved", "Rejected"]
		approved_by: DF.Link | None
		auto_create_commission_entries: DF.Check
		bank_account: DF.Link | None
		city: DF.Data | None
		commission_calculation_method: DF.Literal["Percentage", "Fixed Amount", "Tiered", "Custom"]
		commission_on_delivery: DF.Check
		commission_on_payment: DF.Check
		commission_statement_frequency: DF.Literal["Weekly", "Monthly", "Quarterly", "Yearly"]
		country: DF.Link | None
		created_by: DF.Link | None
		creation_date: DF.Datetime | None
		email: DF.Data | None
		employee: DF.Link | None
		enable_commission: DF.Check
		internal_notes: DF.TextEditor | None
		item_group_commission_rates: DF.Table
		joining_date: DF.Date
		last_modified: DF.Datetime | None
		maximum_commission_amount: DF.Currency | None
		minimum_commission_amount: DF.Currency | None
		mobile_no: DF.Data | None
		modified_by: DF.Link | None
		notes: DF.TextEditor | None
		payment_method: DF.Literal["Bank Transfer", "Cash", "Cheque", "UPI", "Wallet"]
		payment_terms: DF.Literal["Immediate", "Net 15", "Net 30", "Net 45", "Net 60", "Quarterly", "Custom"]
		phone: DF.Data | None
		postal_code: DF.Data | None
		sales_partner: DF.Link | None
		send_commission_statements: DF.Check
		state: DF.Data | None
		status: DF.Literal["Active", "Inactive", "Suspended", "Terminated"]
		tax_id: DF.Data | None
		termination_date: DF.Date | None
		territories: DF.Table
	# end: auto-generated types

	def autoname(self):
		"""Auto generate name based on agent code"""
		if not self.agent_code:
			self.agent_code = frappe.model.naming.make_autoname("AGT-.####")
		self.name = self.agent_code

	def validate(self):
		"""Validate sales agent data"""
		self.validate_dates()
		self.validate_commission_rates()
		self.validate_territories()
		self.validate_contact_details()
		self.set_audit_fields()

	def validate_dates(self):
		"""Validate joining and termination dates"""
		if self.termination_date and self.joining_date > self.termination_date:
			frappe.throw(_("Joining date cannot be after termination date"))
		
		if self.status == "Terminated" and not self.termination_date:
			frappe.throw(_("Termination date is required when status is Terminated"))

	def validate_commission_rates(self):
		"""Validate commission rates"""
		if not self.item_group_commission_rates:
			frappe.throw(_("At least one item group commission rate must be defined"))
		
		item_groups = []
		for rate in self.item_group_commission_rates:
			if not rate.item_group:
				frappe.throw(_("Item group is required for all commission rates"))
			
			if rate.item_group in item_groups:
				frappe.throw(_("Duplicate item group: {0}").format(rate.item_group))
			
			item_groups.append(rate.item_group)
			
			# Validate based on calculation method
			if self.commission_calculation_method == "Percentage":
				if not rate.commission_percentage:
					frappe.throw(_("Commission percentage is required for item group: {0}").format(rate.item_group))
				if rate.commission_percentage < 0 or rate.commission_percentage > 100:
					frappe.throw(_("Commission percentage must be between 0 and 100 for item group: {0}").format(rate.item_group))
			
			elif self.commission_calculation_method == "Fixed Amount":
				if not rate.fixed_amount:
					frappe.throw(_("Fixed amount is required for item group: {0}").format(rate.item_group))
				if rate.fixed_amount < 0:
					frappe.throw(_("Fixed amount cannot be negative for item group: {0}").format(rate.item_group))

	def validate_territories(self):
		"""Validate territory allocations"""
		if self.territories:
			total_allocation = 0
			primary_count = 0
			
			for territory in self.territories:
				if territory.allocation_percentage:
					total_allocation += flt(territory.allocation_percentage)
				
				if territory.is_primary:
					primary_count += 1
			
			if primary_count > 1:
				frappe.throw(_("Only one territory can be marked as primary"))
			
			if total_allocation > 100:
				frappe.throw(_("Total territory allocation cannot exceed 100%"))

	def validate_contact_details(self):
		"""Validate contact details"""
		if self.email and not frappe.utils.validate_email_address(self.email):
			frappe.throw(_("Invalid email address"))

	def set_audit_fields(self):
		"""Set audit fields"""
		if self.is_new():
			self.created_by = frappe.session.user
			self.creation_date = now_datetime()
		
		self.modified_by = frappe.session.user
		self.last_modified = now_datetime()

	def on_submit(self):
		"""Handle submission"""
		self.create_or_link_sales_partner()
		self.set_approval_status()

	def create_or_link_sales_partner(self):
		"""Create or link Sales Partner"""
		if not self.sales_partner:
			# Create new Sales Partner
			sales_partner = frappe.new_doc("Sales Partner")
			sales_partner.partner_name = self.agent_name
			sales_partner.partner_type = "Individual" if self.agent_type == "External" else "Company"
			sales_partner.territory = self.get_primary_territory()
			
			# Set commission rate (average from item groups)
			avg_commission = self.get_average_commission_rate()
			if avg_commission:
				sales_partner.commission_rate = avg_commission
			
			sales_partner.insert()
			self.sales_partner = sales_partner.name
			
			# Update Sales Partner with custom fields
			sales_partner.linked_sales_agent = self.name
			sales_partner.auto_create_commission_entries = self.auto_create_commission_entries
			sales_partner.save()

	def get_primary_territory(self):
		"""Get primary territory"""
		for territory in self.territories:
			if territory.is_primary:
				return territory.territory
		
		# Return first territory if no primary
		if self.territories:
			return self.territories[0].territory
		
		return None

	def get_average_commission_rate(self):
		"""Get average commission rate"""
		if not self.item_group_commission_rates:
			return 0
		
		total_rate = 0
		count = 0
		
		for rate in self.item_group_commission_rates:
			if rate.commission_percentage:
				total_rate += flt(rate.commission_percentage)
				count += 1
		
		return total_rate / count if count > 0 else 0

	def set_approval_status(self):
		"""Set approval status"""
		if not self.approval_status or self.approval_status == "Draft":
			self.approval_status = "Approved"
			self.approved_by = frappe.session.user

	def on_cancel(self):
		"""Handle cancellation"""
		# Check if there are commission entries
		commission_entries = frappe.get_all("Sales Agent Commission Entry",
			filters={"sales_agent": self.name},
			fields=["name"]
		)
		
		if commission_entries:
			frappe.throw(_("Cannot cancel sales agent with existing commission entries"))

	def get_commission_rate_for_item_group(self, item_group, posting_date=None):
		"""Get commission rate for specific item group"""
		if not posting_date:
			posting_date = today()
		
		for rate in self.item_group_commission_rates:
			if rate.item_group == item_group:
				# Check effective dates
				if rate.effective_from and getdate(rate.effective_from) > getdate(posting_date):
					continue
				
				if rate.effective_to and getdate(rate.effective_to) < getdate(posting_date):
					continue
				
				return rate
		
		return None

@frappe.whitelist()
def create_sales_agent_from_partner(sales_partner, method=None):
	"""Create Sales Agent from Sales Partner"""
	if not sales_partner:
		return
	
	# Check if Sales Agent already exists
	existing_agent = frappe.db.get_value("Sales Agent", {"sales_partner": sales_partner.name})
	if existing_agent:
		return
	
	# Create new Sales Agent
	agent = frappe.new_doc("Sales Agent")
	agent.agent_name = sales_partner.partner_name
	agent.sales_partner = sales_partner.name
	agent.joining_date = today()
	agent.agent_type = "External"
	agent.commission_calculation_method = "Percentage"
	
	# Add default commission rate
	if sales_partner.commission_rate:
		# Get all item groups and set same commission rate
		item_groups = frappe.get_all("Item Group", fields=["name"])
		for item_group in item_groups[:5]:  # Add first 5 item groups
			agent.append("item_group_commission_rates", {
				"item_group": item_group.name,
				"commission_percentage": sales_partner.commission_rate,
				"effective_from": today()
			})
	
	# Add territory if available
	if sales_partner.territory:
		agent.append("territories", {
			"territory": sales_partner.territory,
			"is_primary": 1,
			"allocation_percentage": 100,
			"effective_from": today()
		})
	
	agent.insert()
	
	# Update Sales Partner with link
	sales_partner.linked_sales_agent = agent.name
	sales_partner.save()

@frappe.whitelist()
def update_sales_agent_from_partner(sales_partner, method=None):
	"""Update Sales Agent from Sales Partner"""
	if not sales_partner:
		return
	
	# Get linked Sales Agent
	agent_name = frappe.db.get_value("Sales Agent", {"sales_partner": sales_partner.name})
	if not agent_name:
		return
	
	agent = frappe.get_doc("Sales Agent", agent_name)
	
	# Update basic details
	agent.agent_name = sales_partner.partner_name
	
	# Update commission rates if changed
	if sales_partner.commission_rate:
		for rate in agent.item_group_commission_rates:
			if rate.commission_percentage != sales_partner.commission_rate:
				rate.commission_percentage = sales_partner.commission_rate
	
	agent.save()

@frappe.whitelist()
def get_agent_commission_summary(agent_name, from_date=None, to_date=None):
	"""Get commission summary for agent"""
	if not from_date:
		from_date = frappe.utils.add_months(today(), -1)
	if not to_date:
		to_date = today()
	
	summary = frappe.db.sql("""
		SELECT 
			COUNT(*) as total_entries,
			SUM(total_commission_amount) as total_commission,
			SUM(commission_due_amount) as total_due,
			SUM(commission_paid_amount) as total_paid,
			SUM(commission_outstanding_amount) as total_outstanding
		FROM `tabSales Agent Commission Entry`
		WHERE sales_agent = %s
		AND invoice_date BETWEEN %s AND %s
		AND docstatus = 1
	""", (agent_name, from_date, to_date), as_dict=1)
	
	return summary[0] if summary else {}

@frappe.whitelist()
def get_pending_invoices_for_agent(agent_name):
	"""Get pending invoices for agent where commission is due"""
	return frappe.db.sql("""
		SELECT 
			sales_invoice,
			customer,
			invoice_date,
			invoice_amount,
			total_commission_amount,
			commission_status,
			invoice_payment_status,
			invoice_outstanding_amount
		FROM `tabSales Agent Commission Entry`
		WHERE sales_agent = %s
		AND commission_status IN ('Pending Invoice Payment', 'Due for Payment')
		AND docstatus = 1
		ORDER BY invoice_date DESC
	""", (agent_name,), as_dict=1)

@frappe.whitelist()
def approve_sales_agent(agent_name):
	"""Approve sales agent"""
	agent = frappe.get_doc("Sales Agent", agent_name)
	agent.approval_status = "Approved"
	agent.approved_by = frappe.session.user
	agent.save()
	
	frappe.msgprint(_("Sales Agent {0} has been approved").format(agent.agent_name))

@frappe.whitelist()
def reject_sales_agent(agent_name, reason=None):
	"""Reject sales agent"""
	agent = frappe.get_doc("Sales Agent", agent_name)
	agent.approval_status = "Rejected"
	agent.approved_by = frappe.session.user
	
	if reason:
		agent.internal_notes = (agent.internal_notes or "") + f"\n\nRejection Reason: {reason}"
	
	agent.save()
	
	frappe.msgprint(_("Sales Agent {0} has been rejected").format(agent.agent_name))