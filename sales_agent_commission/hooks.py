# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from . import __version__ as app_version

app_name = "sales_agent_commission"
app_title = "Sales Agent Commission"
app_publisher = "Frappe Technologies Pvt. Ltd."
app_description = "Comprehensive Sales Agent Commission Management System"
app_email = "support@frappe.io"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = "/assets/sales_agent_commission/css/sales_agent_commission.css"
app_include_js = "/assets/sales_agent_commission/js/sales_agent_commission.js"

# include js, css files in header of web template
# web_include_css = "/assets/sales_agent_commission/css/sales_agent_commission.css"
# web_include_js = "/assets/sales_agent_commission/js/sales_agent_commission.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "sales_agent_commission/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
#	"methods": "sales_agent_commission.utils.jinja_methods",
#	"filters": "sales_agent_commission.utils.jinja_filters"
# }

# Installation
# ------------

before_install = "sales_agent_commission.install.before_install"
after_install = "sales_agent_commission.install.after_install"

# Uninstallation
# ------------

before_uninstall = "sales_agent_commission.install.before_uninstall"
after_uninstall = "sales_agent_commission.install.after_uninstall"

# Desk Notifications
# -------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "sales_agent_commission.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
#	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Sales Invoice": {
		"on_submit": [
			"sales_agent_commission.overrides.create_agent_commission_entries"
		],
		"on_cancel": [
			"sales_agent_commission.overrides.cancel_agent_commission_entries"
		]
	},
	"Payment Entry": {
		"on_submit": [
			"sales_agent_commission.overrides.check_invoice_payment_reconciliation"
		],
		"on_cancel": [
			"sales_agent_commission.overrides.revert_invoice_payment_reconciliation"
		]
	},
	"Payment Reconciliation": {
		"on_submit": [
			"sales_agent_commission.overrides.update_commission_entries_on_reconciliation"
		]
	}
}

# Scheduled Tasks
# ---------------

scheduler_events = {
	"daily": [
		"sales_agent_commission.tasks.check_agreement_expiry",
		"sales_agent_commission.tasks.update_commission_status_daily"
	],
	"weekly": [
		"sales_agent_commission.tasks.send_commission_statements"
	],
	"monthly": [
		"sales_agent_commission.tasks.generate_monthly_commission_report"
	]
}

# Testing
# -------

# before_tests = "sales_agent_commission.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "sales_agent_commission.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "sales_agent_commission.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]


# User Data Protection
# --------------------

# user_data_fields = [
#	{
#		"doctype": "{doctype_1}",
#		"filter_by": "{filter_by}",
#		"redact_fields": ["{field_1}", "{field_2}"],
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_2}",
#		"filter_by": "{filter_by}",
#		"strict": False,
#	},
#	{
#		"doctype": "{doctype_3}",
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_4}"
#	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"sales_agent_commission.auth.validate"
# ]

# Website Integration
# -------------------

# website_route_rules = [
# 	{"from_route": "/commission/<path:app_path>", "to_route": "commission"},
# ]

# Custom Fields
# -------------

# Add custom fields to existing doctypes
custom_fields = {
	"Sales Partner": [
		{
			"fieldname": "sales_agent_commission_section",
			"fieldtype": "Section Break",
			"label": "Sales Agent Commission",
			"insert_after": "commission_rate"
		},
		{
			"fieldname": "linked_sales_agent",
			"fieldtype": "Link",
			"label": "Linked Sales Agent",
			"options": "Sales Agent",
			"insert_after": "sales_agent_commission_section",
			"read_only": 1
		},
		{
			"fieldname": "auto_create_commission_entries",
			"fieldtype": "Check",
			"label": "Auto Create Commission Entries",
			"insert_after": "linked_sales_agent",
			"default": 1
		}
	],
	"Sales Invoice": [
		{
			"fieldname": "agent_commission_section",
			"fieldtype": "Section Break",
			"label": "Agent Commission Information",
			"insert_after": "terms",
			"collapsible": 1
		},
		{
			"fieldname": "applicable_agents",
			"fieldtype": "Small Text",
			"label": "Applicable Agents",
			"insert_after": "agent_commission_section",
			"read_only": 1,
			"description": "Agents eligible for commission based on territory and customer"
		},
		{
			"fieldname": "commission_entries_created",
			"fieldtype": "Check",
			"label": "Commission Entries Created",
			"insert_after": "applicable_agents",
			"read_only": 1
		},
		{
			"fieldname": "total_commission_amount",
			"fieldtype": "Currency",
			"label": "Total Commission Amount",
			"insert_after": "commission_entries_created",
			"read_only": 1
		}
	],
	"Customer": [
		{
			"fieldname": "sales_agent_section",
			"fieldtype": "Section Break",
			"label": "Sales Agent Information",
			"insert_after": "default_sales_partner",
			"collapsible": 1
		},
		{
			"fieldname": "primary_sales_agent",
			"fieldtype": "Link",
			"label": "Primary Sales Agent",
			"options": "Sales Agent",
			"insert_after": "sales_agent_section"
		},
		{
			"fieldname": "commission_applicable",
			"fieldtype": "Check",
			"label": "Commission Applicable",
			"insert_after": "primary_sales_agent",
			"default": 1
		}
	]
}

# Fixtures
# --------

fixtures = [
	{
		"doctype": "Custom Field",
		"filters": [
			[
				"name",
				"in",
				[
					"Sales Partner-sales_agent_commission_section",
					"Sales Partner-linked_sales_agent",
					"Sales Partner-auto_create_commission_entries",
					"Sales Invoice-agent_commission_section",
					"Sales Invoice-applicable_agents",
					"Sales Invoice-commission_entries_created",
					"Sales Invoice-total_commission_amount",
					"Customer-sales_agent_section",
					"Customer-primary_sales_agent",
					"Customer-commission_applicable"
				]
			]
		]
	}
]