# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class AgentCommissionItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		base_amount: DF.Currency
		commission_amount: DF.Currency
		commission_rate: DF.Float
		item_code: DF.Link | None
		item_group: DF.Link
		item_name: DF.Data | None
		qty: DF.Float
	# end: auto-generated types

	pass