# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _


class CustomDesk:
	"""Custom Desk class to add Sales Commission menu"""
	
	def __init__(self):
		pass
	
	def get_selling_menu(self):
		"""Get selling menu with Sales Commission submenu"""
		from frappe.desk.doctype.desktop_icon.desktop_icon import get_desktop_icons
		
		# Get original selling menu
		original_menu = get_desktop_icons("Selling")
		
		# Add Sales Commission submenu
		sales_commission_menu = {
			"label": _("Sales Commission"),
			"icon": "fa fa-percentage",
			"items": [
				{
					"type": "doctype",
					"name": "Agent Commission Rule",
					"label": _("Commission Rules"),
					"description": _("Define commission rules for agents")
				},
				{
					"type": "doctype",
					"name": "Agent Customer Assignment",
					"label": _("Customer Assignments"),
					"description": _("Assign customers to agents")
				},
				{
					"type": "doctype",
					"name": "Agent Commission Entry",
					"label": _("Commission Entries"),
					"description": _("View commission entries")
				},
				{
					"type": "doctype",
					"name": "Commission Payment Voucher",
					"label": _("Payment Vouchers"),
					"description": _("Create commission payments")
				},
				{
					"type": "separator"
				},
				{
					"type": "report",
					"name": "Agent Commission Summary",
					"label": _("Commission Summary"),
					"description": _("Commission summary report"),
					"is_query_report": True
				},
				{
					"type": "report",
					"name": "Agent Commission Payable",
					"label": _("Commission Payable"),
					"description": _("Outstanding commission report"),
					"is_query_report": True
				}
			]
		}
		
		# Add to original menu
		original_menu.append(sales_commission_menu)
		
		return original_menu


def get_selling_menu():
	"""Hook function to get selling menu with Sales Commission"""
	custom_desk = CustomDesk()
	return custom_desk.get_selling_menu()