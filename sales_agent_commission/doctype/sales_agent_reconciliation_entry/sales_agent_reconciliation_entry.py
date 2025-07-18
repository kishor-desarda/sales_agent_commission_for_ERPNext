# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SalesAgentReconciliationEntry(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		commission_due_amount: DF.Currency | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		reconciliation_date: DF.Date | None
		reconciliation_entry: DF.Link
		reconciliation_status: DF.Data | None
		reconciled_amount: DF.Currency | None
	# end: auto-generated types

	pass