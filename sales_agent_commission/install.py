# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def before_install():
	"""Before install hook"""
	pass


def after_install():
	"""After install hook"""
	install()


def before_uninstall():
	"""Before uninstall hook"""
	pass


def after_uninstall():
	"""After uninstall hook"""
	uninstall()


def install():
	"""Install the app"""
	# Create custom fields if needed
	create_custom_fields()
	
	# Create naming series
	create_naming_series()
	
	# Create default permissions
	create_default_permissions()
	
	frappe.db.commit()


def create_custom_fields():
	"""Create custom fields if needed"""
	pass


def create_naming_series():
	"""Create naming series for the app"""
	naming_series = [
		{
			"doctype": "Agent Commission Rule",
			"prefix": "ACR-.YYYY.-",
			"current": 0
		},
		{
			"doctype": "Agent Commission Entry",
			"prefix": "ACE-.YYYY.-",
			"current": 0
		},
		{
			"doctype": "Commission Payment Voucher",
			"prefix": "CPV-.YYYY.-",
			"current": 0
		},
		{
			"doctype": "Agent Customer Assignment",
			"prefix": "ACA-.YYYY.-",
			"current": 0
		}
	]
	
	for series in naming_series:
		if not frappe.db.exists("Naming Series", series["prefix"]):
			frappe.get_doc({
				"doctype": "Naming Series",
				"naming_series": series["prefix"],
				"current": series["current"]
			}).insert()


def create_default_permissions():
	"""Create default permissions for the app"""
	# Sales Manager role permissions
	sales_manager_permissions = [
		"Agent Commission Rule",
		"Agent Commission Entry",
		"Commission Payment Voucher",
		"Agent Customer Assignment"
	]
	
	for doctype in sales_manager_permissions:
		if not frappe.db.exists("Custom DocPerm", {"parent": doctype, "role": "Sales Manager"}):
			frappe.get_doc({
				"doctype": "Custom DocPerm",
				"parent": doctype,
				"role": "Sales Manager",
				"permlevel": 0,
				"select": 1,
				"read": 1,
				"write": 1,
				"create": 1,
				"delete": 1,
				"submit": 1,
				"cancel": 1,
				"amend": 1,
				"report": 1,
				"export": 1,
				"share": 1,
				"print": 1,
				"email": 1
			}).insert()


def uninstall():
	"""Uninstall the app"""
	# Remove custom fields
	remove_custom_fields()
	
	# Remove naming series
	remove_naming_series()
	
	frappe.db.commit()


def remove_custom_fields():
	"""Remove custom fields"""
	pass


def remove_naming_series():
	"""Remove naming series"""
	naming_series = [
		"ACR-.YYYY.-",
		"ACE-.YYYY.-",
		"CPV-.YYYY.-",
		"ACA-.YYYY.-"
	]
	
	for series in naming_series:
		if frappe.db.exists("Naming Series", series):
			frappe.delete_doc("Naming Series", series)