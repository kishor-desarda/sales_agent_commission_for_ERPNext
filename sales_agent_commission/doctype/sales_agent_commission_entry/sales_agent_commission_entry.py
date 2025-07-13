# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate, today, now_datetime, cstr


class SalesAgentCommissionEntry(Document):
	def validate(self):
		"""Validate commission entry"""
		self.validate_sales_invoice()
		self.validate_sales_agent()
		self.calculate_commission()
		self.update_payment_status()
		self.set_audit_details()

	def validate_sales_invoice(self):
		"""Validate sales invoice"""
		if not self.sales_invoice:
			frappe.throw(_("Sales Invoice is required"))
		
		# Check if sales invoice exists and is submitted
		si_doc = frappe.get_doc("Sales Invoice", self.sales_invoice)
		if si_doc.docstatus != 1:
			frappe.throw(_("Sales Invoice must be submitted"))

	def validate_sales_agent(self):
		"""Validate sales agent"""
		if not self.sales_agent:
			frappe.throw(_("Sales Agent is required"))
		
		# Check if sales agent is active
		agent_doc = frappe.get_doc("Sales Agent", self.sales_agent)
		if agent_doc.status != "Active":
			frappe.throw(_("Sales Agent must be active"))
		
		if not agent_doc.enable_commission:
			frappe.throw(_("Commission is not enabled for this Sales Agent"))

	def calculate_commission(self):
		"""Calculate commission based on invoice items"""
		if not self.commission_items:
			self.create_commission_items()
		
		total_commission = 0
		total_base_amount = 0
		
		for item in self.commission_items:
			total_commission += flt(item.commission_amount)
			total_base_amount += flt(item.base_amount)
		
		self.total_commission_amount = total_commission
		self.total_base_amount = total_base_amount
		
		# Calculate company currency amount
		if self.exchange_rate:
			self.commission_amount_company_currency = total_commission * flt(self.exchange_rate)
		else:
			self.commission_amount_company_currency = total_commission
		
		# Calculate average commission percentage
		if total_base_amount > 0:
			self.commission_percentage_avg = (total_commission / total_base_amount) * 100

	def create_commission_items(self):
		"""Create commission items from sales invoice"""
		si_doc = frappe.get_doc("Sales Invoice", self.sales_invoice)
		agent_doc = frappe.get_doc("Sales Agent", self.sales_agent)
		
		self.commission_items = []
		
		for item in si_doc.items:
			# Get commission rate for item group
			commission_rate = agent_doc.get_commission_rate_for_item_group(
				item.item_group, si_doc.posting_date
			)
			
			if commission_rate:
				commission_amount = self.calculate_item_commission(
					item, commission_rate, agent_doc.commission_calculation_method
				)
				
				self.append("commission_items", {
					"item_code": item.item_code,
					"item_name": item.item_name,
					"item_group": item.item_group,
					"qty": item.qty,
					"rate": item.rate,
					"amount": item.amount,
					"base_amount": item.base_amount,
					"commission_rate": commission_rate.commission_percentage or 0,
					"commission_amount": commission_amount,
					"calculation_method": agent_doc.commission_calculation_method
				})

	def calculate_item_commission(self, item, commission_rate, calculation_method):
		"""Calculate commission for individual item"""
		if calculation_method == "Percentage":
			commission = flt(item.base_amount) * flt(commission_rate.commission_percentage) / 100
		elif calculation_method == "Fixed Amount":
			commission = flt(commission_rate.fixed_amount) * flt(item.qty)
		elif calculation_method == "Tiered":
			commission = self.calculate_tiered_commission(item, commission_rate)
		else:
			commission = 0
		
		# Apply min/max limits
		if commission_rate.minimum_amount and commission < commission_rate.minimum_amount:
			commission = commission_rate.minimum_amount
		
		if commission_rate.maximum_amount and commission > commission_rate.maximum_amount:
			commission = commission_rate.maximum_amount
		
		return commission

	def calculate_tiered_commission(self, item, commission_rate):
		"""Calculate tiered commission"""
		amount = flt(item.base_amount)
		commission = 0
		
		for tier in commission_rate.tiered_rates:
			tier_from = flt(tier.from_amount)
			tier_to = flt(tier.to_amount) if tier.to_amount else float('inf')
			
			if amount > tier_from:
				tier_amount = min(amount, tier_to) - tier_from
				commission += tier_amount * flt(tier.commission_percentage) / 100
		
		return commission

	def update_payment_status(self):
		"""Update payment status based on invoice payments"""
		# Get invoice payment status
		si_doc = frappe.get_doc("Sales Invoice", self.sales_invoice)
		
		self.invoice_outstanding_amount = si_doc.outstanding_amount
		
		if si_doc.outstanding_amount <= 0:
			self.invoice_payment_status = "Paid"
		elif si_doc.outstanding_amount < si_doc.grand_total:
			self.invoice_payment_status = "Partially Paid"
		else:
			self.invoice_payment_status = "Unpaid"
		
		# Update commission due amount based on payment
		self.update_commission_due_amount()

	def update_commission_due_amount(self):
		"""Update commission due amount based on payment reconciliation"""
		si_doc = frappe.get_doc("Sales Invoice", self.sales_invoice)
		
		# Calculate paid percentage
		paid_amount = flt(si_doc.grand_total) - flt(si_doc.outstanding_amount)
		paid_percentage = (paid_amount / flt(si_doc.grand_total)) * 100 if si_doc.grand_total > 0 else 0
		
		# Commission due is based on paid percentage
		self.commission_due_amount = (flt(self.total_commission_amount) * paid_percentage) / 100
		
		# Commission outstanding is total minus paid
		self.commission_outstanding_amount = flt(self.total_commission_amount) - flt(self.commission_paid_amount)
		
		# Update commission status
		self.update_commission_status()

	def update_commission_status(self):
		"""Update commission status"""
		agent_doc = frappe.get_doc("Sales Agent", self.sales_agent)
		
		if self.invoice_payment_status == "Unpaid":
			self.commission_status = "Pending Invoice Payment"
			self.commission_payment_status = "Not Due"
		elif self.invoice_payment_status in ["Partially Paid", "Paid"]:
			if agent_doc.commission_on_payment:
				self.commission_status = "Due for Payment"
				if self.commission_due_amount > 0:
					self.commission_payment_status = "Due"
			else:
				self.commission_status = "Pending Invoice Payment"
				self.commission_payment_status = "Not Due"
		
		# Update based on commission payments
		if flt(self.commission_paid_amount) >= flt(self.commission_due_amount):
			self.commission_payment_status = "Paid"
		elif flt(self.commission_paid_amount) > 0:
			self.commission_payment_status = "Partially Paid"

	def set_audit_details(self):
		"""Set audit details"""
		creation_details = f"""
		Created: {now_datetime()}
		User: {frappe.session.user}
		Sales Invoice: {self.sales_invoice}
		Sales Agent: {self.sales_agent}
		Commission Method: {frappe.get_value('Sales Agent', self.sales_agent, 'commission_calculation_method')}
		"""
		
		calculation_details = f"""
		Total Invoice Amount: {self.invoice_amount}
		Total Commission: {self.total_commission_amount}
		Commission Due: {self.commission_due_amount}
		Commission Outstanding: {self.commission_outstanding_amount}
		Average Commission %: {self.commission_percentage_avg}
		"""
		
		self.creation_details = creation_details
		self.calculation_details = calculation_details


# Document Event Handlers
@frappe.whitelist()
def create_commission_entries(doc, method=None):
	"""Create commission entries when Sales Invoice is submitted"""
	if not doc.sales_agent:
		return
	
	# Check if agent has commission enabled
	agent_doc = frappe.get_doc("Sales Agent", doc.sales_agent)
	if not agent_doc.enable_commission or not agent_doc.auto_create_commission_entries:
		return
	
	# Check if commission entry already exists
	existing_entry = frappe.get_all("Sales Agent Commission Entry",
		filters={"sales_invoice": doc.name, "sales_agent": doc.sales_agent},
		fields=["name"]
	)
	
	if existing_entry:
		return
	
	# Create commission entry
	commission_entry = frappe.new_doc("Sales Agent Commission Entry")
	commission_entry.sales_agent = doc.sales_agent
	commission_entry.sales_invoice = doc.name
	commission_entry.insert()
	commission_entry.submit()
	
	# Update sales invoice
	doc.commission_entries_created = 1
	doc.save()
	
	frappe.msgprint(_("Commission entry created: {0}").format(commission_entry.name))

@frappe.whitelist()
def cancel_commission_entries(doc, method=None):
	"""Cancel commission entries when Sales Invoice is cancelled"""
	commission_entries = frappe.get_all("Sales Agent Commission Entry",
		filters={"sales_invoice": doc.name},
		fields=["name"]
	)
	
	for entry in commission_entries:
		commission_doc = frappe.get_doc("Sales Agent Commission Entry", entry.name)
		if commission_doc.docstatus == 1:
			commission_doc.cancel()

@frappe.whitelist()
def update_commission_payment_status(doc, method=None):
	"""Update commission payment status when Payment Entry is submitted"""
	if doc.doctype != "Payment Entry":
		return
	
	# Get sales invoices from payment entry
	for reference in doc.references:
		if reference.reference_doctype == "Sales Invoice":
			update_commission_entries_for_invoice(reference.reference_name)

@frappe.whitelist()
def revert_commission_payment_status(doc, method=None):
	"""Revert commission payment status when Payment Entry is cancelled"""
	if doc.doctype != "Payment Entry":
		return
	
	# Get sales invoices from payment entry
	for reference in doc.references:
		if reference.reference_doctype == "Sales Invoice":
			update_commission_entries_for_invoice(reference.reference_name)

@frappe.whitelist()
def update_commission_due_status(doc, method=None):
	"""Update commission due status when Payment Reconciliation is submitted"""
	if doc.doctype != "Payment Reconciliation":
		return
	
	# Update commission entries for reconciled invoices
	for entry in doc.allocation:
		if entry.reference_type == "Sales Invoice":
			update_commission_entries_for_invoice(entry.reference_name)

@frappe.whitelist()
def revert_commission_due_status(doc, method=None):
	"""Revert commission due status when Payment Reconciliation is cancelled"""
	if doc.doctype != "Payment Reconciliation":
		return
	
	# Update commission entries for reconciled invoices
	for entry in doc.allocation:
		if entry.reference_type == "Sales Invoice":
			update_commission_entries_for_invoice(entry.reference_name)

def update_commission_entries_for_invoice(sales_invoice):
	"""Update all commission entries for a sales invoice"""
	commission_entries = frappe.get_all("Sales Agent Commission Entry",
		filters={"sales_invoice": sales_invoice, "docstatus": 1},
		fields=["name"]
	)
	
	for entry in commission_entries:
		commission_doc = frappe.get_doc("Sales Agent Commission Entry", entry.name)
		commission_doc.update_payment_status()
		commission_doc.save()

@frappe.whitelist()
def update_commission_status_daily():
	"""Daily scheduler to update commission status"""
	# Get all submitted commission entries
	commission_entries = frappe.get_all("Sales Agent Commission Entry",
		filters={"docstatus": 1},
		fields=["name"]
	)
	
	for entry in commission_entries:
		try:
			commission_doc = frappe.get_doc("Sales Agent Commission Entry", entry.name)
			commission_doc.update_payment_status()
			commission_doc.save()
		except Exception as e:
			frappe.log_error(f"Error updating commission entry {entry.name}: {str(e)}")

@frappe.whitelist()
def send_commission_statements():
	"""Weekly scheduler to send commission statements"""
	# Get all active agents who want statements
	agents = frappe.get_all("Sales Agent",
		filters={"status": "Active", "send_commission_statements": 1},
		fields=["name", "agent_name", "email", "commission_statement_frequency"]
	)
	
	for agent in agents:
		try:
			send_agent_commission_statement(agent.name)
		except Exception as e:
			frappe.log_error(f"Error sending commission statement to {agent.name}: {str(e)}")

def send_agent_commission_statement(agent_name):
	"""Send commission statement to agent"""
	agent_doc = frappe.get_doc("Sales Agent", agent_name)
	
	if not agent_doc.email:
		return
	
	# Get commission summary
	from_date = frappe.utils.add_months(today(), -1)
	to_date = today()
	
	commission_entries = frappe.get_all("Sales Agent Commission Entry",
		filters={
			"sales_agent": agent_name,
			"invoice_date": ["between", [from_date, to_date]],
			"docstatus": 1
		},
		fields=["*"]
	)
	
	if not commission_entries:
		return
	
	# Send email with commission statement
	subject = f"Commission Statement - {agent_doc.agent_name}"
	
	# Create email content
	content = f"""
	Dear {agent_doc.agent_name},
	
	Please find your commission statement for the period {from_date} to {to_date}.
	
	Commission Entries: {len(commission_entries)}
	Total Commission: {sum([flt(entry.get('total_commission_amount', 0)) for entry in commission_entries])}
	Commission Due: {sum([flt(entry.get('commission_due_amount', 0)) for entry in commission_entries])}
	Commission Outstanding: {sum([flt(entry.get('commission_outstanding_amount', 0)) for entry in commission_entries])}
	
	Best regards,
	Sales Team
	"""
	
	frappe.sendmail(
		recipients=[agent_doc.email],
		subject=subject,
		content=content
	)