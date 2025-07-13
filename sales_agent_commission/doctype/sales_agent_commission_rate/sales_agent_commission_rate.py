# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SalesAgentCommissionRate(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		commission_percentage: DF.Float | None
		effective_from: DF.Date
		effective_to: DF.Date | None
		fixed_amount: DF.Currency | None
		item_group: DF.Link
		maximum_amount: DF.Currency | None
		minimum_amount: DF.Currency | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		tiered_rates: DF.Table | None
	# end: auto-generated types

	pass