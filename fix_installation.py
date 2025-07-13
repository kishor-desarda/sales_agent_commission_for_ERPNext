#!/usr/bin/env python3
"""
Sales Agent Commission - Installation Fix Script
This script automatically fixes common installation issues.
"""

import os
import sys
import json
from pathlib import Path

def create_init_files():
    """Create missing __init__.py files"""
    print("Creating missing __init__.py files...")
    
    # Main doctype __init__.py
    init_content = '''# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt'''
    
    doctype_dirs = [
        "sales_agent_commission/doctype",
        "sales_agent_commission/doctype/sales_agent",
        "sales_agent_commission/doctype/sales_agent_commission_entry",
        "sales_agent_commission/doctype/sales_agent_territory",
        "sales_agent_commission/doctype/sales_agent_commission_rate",
        "sales_agent_commission/doctype/sales_agent_commission_tier",
        "sales_agent_commission/doctype/sales_agent_commission_item",
        "sales_agent_commission/doctype/sales_agent_payment_entry",
        "sales_agent_commission/doctype/sales_agent_reconciliation_entry",
        "sales_agent_commission/doctype/sales_agent_customer_assignment",
        "sales_agent_commission/doctype/commission_payment_voucher",
        "sales_agent_commission/doctype/commission_payment_item"
    ]
    
    for dir_path in doctype_dirs:
        init_file = os.path.join(dir_path, "__init__.py")
        if not os.path.exists(init_file):
            os.makedirs(dir_path, exist_ok=True)
            with open(init_file, 'w') as f:
                f.write(init_content)
            print(f"Created: {init_file}")

def create_missing_python_files():
    """Create missing Python files for child tables"""
    print("Creating missing Python files...")
    
    child_tables = [
        {
            "name": "sales_agent_territory",
            "class": "SalesAgentTerritory",
            "fields": [
                "allocation_percentage: DF.Float | None",
                "effective_from: DF.Date",
                "effective_to: DF.Date | None",
                "is_primary: DF.Check",
                "parent: DF.Data",
                "parentfield: DF.Data",
                "parenttype: DF.Data",
                "territory: DF.Link"
            ]
        },
        {
            "name": "sales_agent_commission_rate",
            "class": "SalesAgentCommissionRate",
            "fields": [
                "commission_percentage: DF.Float | None",
                "effective_from: DF.Date",
                "effective_to: DF.Date | None",
                "fixed_amount: DF.Currency | None",
                "item_group: DF.Link",
                "maximum_amount: DF.Currency | None",
                "minimum_amount: DF.Currency | None",
                "parent: DF.Data",
                "parentfield: DF.Data",
                "parenttype: DF.Data",
                "tiered_rates: DF.Table | None"
            ]
        },
        {
            "name": "sales_agent_commission_tier",
            "class": "SalesAgentCommissionTier",
            "fields": [
                "commission_percentage: DF.Float",
                "from_amount: DF.Currency",
                "parent: DF.Data",
                "parentfield: DF.Data",
                "parenttype: DF.Data",
                "to_amount: DF.Currency | None"
            ]
        },
        {
            "name": "sales_agent_commission_item",
            "class": "SalesAgentCommissionItem",
            "fields": [
                "amount: DF.Currency | None",
                "base_amount: DF.Currency | None",
                "calculation_method: DF.Data | None",
                "commission_amount: DF.Currency | None",
                "commission_rate: DF.Float | None",
                "item_code: DF.Link",
                "item_group: DF.Link | None",
                "item_name: DF.Data | None",
                "parent: DF.Data",
                "parentfield: DF.Data",
                "parenttype: DF.Data",
                "qty: DF.Float | None",
                "rate: DF.Currency | None"
            ]
        },
        {
            "name": "sales_agent_payment_entry",
            "class": "SalesAgentPaymentEntry",
            "fields": [
                "allocated_amount: DF.Currency | None",
                "parent: DF.Data",
                "parentfield: DF.Data",
                "parenttype: DF.Data",
                "payment_amount: DF.Currency | None",
                "payment_date: DF.Date | None",
                "payment_entry: DF.Link",
                "payment_status: DF.Data | None"
            ]
        },
        {
            "name": "sales_agent_reconciliation_entry",
            "class": "SalesAgentReconciliationEntry",
            "fields": [
                "commission_due_amount: DF.Currency | None",
                "parent: DF.Data",
                "parentfield: DF.Data",
                "parenttype: DF.Data",
                "reconciliation_date: DF.Date | None",
                "reconciliation_entry: DF.Link",
                "reconciliation_status: DF.Data | None",
                "reconciled_amount: DF.Currency | None"
            ]
        },
        {
            "name": "commission_payment_item",
            "class": "CommissionPaymentItem",
            "fields": [
                "commission_amount: DF.Currency | None",
                "commission_entry: DF.Link",
                "paid_amount: DF.Currency | None",
                "parent: DF.Data",
                "parentfield: DF.Data",
                "parenttype: DF.Data",
                "sales_agent: DF.Link | None",
                "sales_invoice: DF.Link | None"
            ]
        }
    ]
    
    for table in child_tables:
        py_file = f"sales_agent_commission/doctype/{table['name']}/{table['name']}.py"
        if not os.path.exists(py_file):
            content = f'''# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class {table['class']}(Document):
\t# begin: auto-generated types
\t# This code is auto-generated. Do not modify anything in this block.

\tfrom typing import TYPE_CHECKING

\tif TYPE_CHECKING:
\t\tfrom frappe.types import DF

\t\t{chr(10).join([f"\t\t{field}" for field in table['fields']])}
\t# end: auto-generated types

\tpass'''
            
            with open(py_file, 'w') as f:
                f.write(content)
            print(f"Created: {py_file}")

def verify_app_structure():
    """Verify app structure"""
    print("Verifying app structure...")
    
    required_files = [
        "sales_agent_commission/__init__.py",
        "sales_agent_commission/hooks.py",
        "sales_agent_commission/modules.txt",
        "sales_agent_commission/sales_agent_commission/__init__.py",
        "setup.py",
        "requirements.txt",
        "MANIFEST.in"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("Missing required files:")
        for file_path in missing_files:
            print(f"  - {file_path}")
        return False
    
    print("App structure verified ✓")
    return True

def create_missing_json_files():
    """Create missing JSON files for child tables"""
    print("Creating missing JSON files...")
    
    # Check if commission_payment_item.json exists
    json_file = "sales_agent_commission/doctype/commission_payment_item/commission_payment_item.json"
    if not os.path.exists(json_file):
        json_content = {
            "actions": [],
            "allow_copy": 0,
            "allow_events_in_timeline": 0,
            "allow_guest_to_view": 0,
            "allow_import": 0,
            "allow_rename": 0,
            "autoname": "field:commission_entry",
            "beta": 0,
            "creation": "2024-01-01 00:00:00",
            "custom": 0,
            "description": "Commission payment item details",
            "docstatus": 0,
            "doctype": "DocType",
            "document_type": "Child Table",
            "editable_grid": 1,
            "engine": "InnoDB",
            "field_order": [
                "commission_entry",
                "sales_agent",
                "sales_invoice",
                "commission_amount",
                "paid_amount"
            ],
            "fields": [
                {
                    "fieldname": "commission_entry",
                    "fieldtype": "Link",
                    "in_list_view": 1,
                    "label": "Commission Entry",
                    "options": "Sales Agent Commission Entry",
                    "reqd": 1
                },
                {
                    "fieldname": "sales_agent",
                    "fieldtype": "Link",
                    "in_list_view": 1,
                    "label": "Sales Agent",
                    "options": "Sales Agent",
                    "read_only": 1
                },
                {
                    "fieldname": "sales_invoice",
                    "fieldtype": "Link",
                    "label": "Sales Invoice",
                    "options": "Sales Invoice",
                    "read_only": 1
                },
                {
                    "fieldname": "commission_amount",
                    "fieldtype": "Currency",
                    "in_list_view": 1,
                    "label": "Commission Amount",
                    "read_only": 1
                },
                {
                    "fieldname": "paid_amount",
                    "fieldtype": "Currency",
                    "in_list_view": 1,
                    "label": "Paid Amount",
                    "reqd": 1
                }
            ],
            "istable": 1,
            "links": [],
            "modified": "2024-01-01 00:00:00",
            "modified_by": "Administrator",
            "module": "Sales Agent Commission",
            "name": "Commission Payment Item",
            "owner": "Administrator",
            "permissions": [],
            "sort_field": "modified",
            "sort_order": "DESC",
            "states": [],
            "track_changes": 0,
            "track_seen": 0,
            "track_views": 0
        }
        
        os.makedirs(os.path.dirname(json_file), exist_ok=True)
        with open(json_file, 'w') as f:
            json.dump(json_content, f, indent=1)
        print(f"Created: {json_file}")

def fix_permissions():
    """Fix file permissions"""
    print("Fixing file permissions...")
    
    # Make Python files executable
    for root, dirs, files in os.walk("sales_agent_commission"):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                os.chmod(file_path, 0o755)

def main():
    """Main function"""
    print("🔧 Sales Agent Commission - Installation Fix Script")
    print("=" * 50)
    
    if not os.path.exists("sales_agent_commission"):
        print("❌ Error: sales_agent_commission directory not found!")
        print("Please run this script from the app root directory.")
        sys.exit(1)
    
    try:
        # Step 1: Create missing __init__.py files
        create_init_files()
        
        # Step 2: Create missing Python files
        create_missing_python_files()
        
        # Step 3: Create missing JSON files
        create_missing_json_files()
        
        # Step 4: Verify app structure
        verify_app_structure()
        
        # Step 5: Fix permissions
        fix_permissions()
        
        print("\n✅ Installation fixes completed successfully!")
        print("\nNext steps:")
        print("1. Run: bench --site your-site migrate")
        print("2. Run: bench restart")
        print("3. Check if Sales Commission appears in sidebar")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()