# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CommissionPaymentItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		commission_amount: DF.Currency
		commission_entry: DF.Link
		customer: DF.Link | None
		invoice_date: DF.Date | None
		paid_amount: DF.Currency
		sales_invoice: DF.Link | None
	# end: auto-generated types

	pass