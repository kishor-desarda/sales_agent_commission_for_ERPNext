# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class CommissionPaymentItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		commission_amount: DF.Currency | None
		commission_entry: DF.Link
		customer: DF.Link | None
		item_group: DF.Link | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		payment_status: DF.Data | None
		sales_invoice: DF.Link | None
	# end: auto-generated types

	pass