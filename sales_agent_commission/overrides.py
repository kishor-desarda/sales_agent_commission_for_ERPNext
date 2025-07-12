# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def get_sales_commission_menu():
	"""Get Sales Commission menu items"""
	return [
		{
			"label": _("Commission Rules"),
			"icon": "fa fa-cog",
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
				}
			]
		},
		{
			"label": _("Commission Entries"),
			"icon": "fa fa-list",
			"items": [
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
				}
			]
		},
		{
			"label": _("Reports"),
			"icon": "fa fa-chart-bar",
			"items": [
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
	]

def get_selling_menu():
	"""Override Selling menu to include Sales Commission"""
	# Get original selling menu
	original_menu = frappe.get_hooks("selling_menu") or []
	
	# Add Sales Commission submenu
	sales_commission_menu = {
		"label": _("Sales Commission"),
		"icon": "fa fa-percentage",
		"items": get_sales_commission_menu()
	}
	
	# Insert after existing items
	original_menu.append(sales_commission_menu)
	
	return original_menu

# Hook to override selling menu
def get_selling_menu_override():
	return get_selling_menu()

# Add to hooks
frappe.hooks.selling_menu = get_selling_menu_override