# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SalesAgentCommissionItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amount: DF.Currency | None
		base_amount: DF.Currency | None
		calculation_method: DF.Data | None
		commission_amount: DF.Currency | None
		commission_rate: DF.Float | None
		item_code: DF.Link
		item_group: DF.Link | None
		item_name: DF.Data | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		qty: DF.Float | None
		rate: DF.Currency | None
	# end: auto-generated types

	pass