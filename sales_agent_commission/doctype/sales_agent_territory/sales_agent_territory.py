# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SalesAgentTerritory(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		allocation_percentage: DF.Float | None
		effective_from: DF.Date
		effective_to: DF.Date | None
		is_primary: DF.Check
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		territory: DF.Link
	# end: auto-generated types

	pass