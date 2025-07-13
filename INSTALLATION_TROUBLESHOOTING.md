# Sales Agent Commission - Installation Troubleshooting Guide

## 🔧 **Common Installation Issues & Solutions**

### **Issue 1: Missing Python Files for Doctypes**

**Error**: `ImportError: cannot import name 'SalesAgentTerritory' from 'sales_agent_commission.doctype.sales_agent_territory'`

**Solution**: Ensure all doctypes have the required files:

```bash
# Check if all required files exist
find sales_agent_commission/doctype -name "*.py" | sort
find sales_agent_commission/doctype -name "*.json" | sort
find sales_agent_commission/doctype -name "__init__.py" | sort
```

**Required Structure for Each Doctype**:
```
sales_agent_commission/doctype/
├── __init__.py
├── sales_agent/
│   ├── __init__.py
│   ├── sales_agent.py
│   └── sales_agent.json
├── sales_agent_commission_entry/
│   ├── __init__.py
│   ├── sales_agent_commission_entry.py
│   └── sales_agent_commission_entry.json
├── sales_agent_territory/
│   ├── __init__.py
│   ├── sales_agent_territory.py
│   └── sales_agent_territory.json
├── sales_agent_commission_rate/
│   ├── __init__.py
│   ├── sales_agent_commission_rate.py
│   └── sales_agent_commission_rate.json
├── sales_agent_commission_tier/
│   ├── __init__.py
│   ├── sales_agent_commission_tier.py
│   └── sales_agent_commission_tier.json
├── sales_agent_commission_item/
│   ├── __init__.py
│   ├── sales_agent_commission_item.py
│   └── sales_agent_commission_item.json
├── sales_agent_payment_entry/
│   ├── __init__.py
│   ├── sales_agent_payment_entry.py
│   └── sales_agent_payment_entry.json
├── sales_agent_reconciliation_entry/
│   ├── __init__.py
│   ├── sales_agent_reconciliation_entry.py
│   └── sales_agent_reconciliation_entry.json
├── sales_agent_customer_assignment/
│   ├── __init__.py
│   ├── sales_agent_customer_assignment.py
│   └── sales_agent_customer_assignment.json
└── commission_payment_voucher/
    ├── __init__.py
    ├── commission_payment_voucher.py
    └── commission_payment_voucher.json
```

### **Issue 2: Module Structure Problems**

**Error**: `ModuleNotFoundError: No module named 'sales_agent_commission'`

**Solution**: Verify app structure:

```bash
# Check app structure
ls -la sales_agent_commission/
ls -la sales_agent_commission/sales_agent_commission/
```

**Required App Structure**:
```
sales_agent_commission/
├── __init__.py
├── hooks.py
├── setup.py
├── requirements.txt
├── MANIFEST.in
├── modules.txt
├── patches.txt
├── sales_agent_commission/
│   ├── __init__.py
│   ├── doctype/
│   ├── report/
│   ├── workspace/
│   └── public/
└── README.md
```

### **Issue 3: Frappe Framework Import Errors**

**Error**: `Import "frappe" could not be resolved`

**Solution**: These are false positive linter errors. The Frappe framework is available at runtime. To suppress:

1. **For VS Code**: Add to `.vscode/settings.json`:
```json
{
    "python.linting.pylintArgs": [
        "--disable=import-error"
    ]
}
```

2. **For PyCharm**: Mark `frappe-bench` as source root.

### **Issue 4: Workspace Not Appearing**

**Error**: Sales Commission not visible in sidebar

**Solution**:
```bash
# Clear cache and restart
bench --site your-site clear-cache
bench --site your-site clear-website-cache
bench restart

# Rebuild if needed
bench --site your-site build
```

### **Issue 5: Custom Fields Not Created**

**Error**: Custom fields missing on Sales Partner, Sales Invoice, Customer

**Solution**:
```bash
# Migrate and reload
bench --site your-site migrate
bench --site your-site reload-doc sales_agent_commission
```

### **Issue 6: Naming Series Issues**

**Error**: `Cannot create document: Naming Series not found`

**Solution**: Manually create naming series:
```bash
bench --site your-site console
```

```python
# Create naming series
import frappe

naming_series = [
    {"name": "AGT-.####", "doctype": "Sales Agent"},
    {"name": "SACE-.YYYY.-", "doctype": "Sales Agent Commission Entry"},
    {"name": "CPV-.YYYY.-", "doctype": "Commission Payment Voucher"},
    {"name": "SACA-.YYYY.-", "doctype": "Sales Agent Customer Assignment"}
]

for series in naming_series:
    if not frappe.db.exists("Naming Series", series["name"]):
        doc = frappe.new_doc("Naming Series")
        doc.name = series["name"]
        doc.prefix = series["name"]
        doc.insert()
```

### **Issue 7: Permission Errors**

**Error**: `You don't have permission to access this resource`

**Solution**: Set up permissions:
```bash
bench --site your-site console
```

```python
import frappe

# Create default permissions
doctypes = [
    "Sales Agent",
    "Sales Agent Commission Entry", 
    "Commission Payment Voucher",
    "Sales Agent Customer Assignment"
]

roles = [
    {"role": "Sales Manager", "perms": ["create", "read", "write", "delete", "submit", "cancel"]},
    {"role": "Sales User", "perms": ["read", "write"]},
    {"role": "Accounts Manager", "perms": ["create", "read", "write", "submit"]}
]

for doctype in doctypes:
    for role_perm in roles:
        for perm in role_perm["perms"]:
            frappe.permissions.add_permission(doctype, role_perm["role"], perm)
```

### **Issue 8: Database Migration Errors**

**Error**: `Table 'tabSales Agent' doesn't exist`

**Solution**: Force migration:
```bash
# Reset and migrate
bench --site your-site migrate --reset-permissions
bench --site your-site reload-doc sales_agent_commission sales_agent
```

### **Issue 9: Hook Configuration Issues**

**Error**: Document events not firing

**Solution**: Verify hooks.py configuration:
```python
# Check hooks.py has correct format
doc_events = {
    "Sales Invoice": {
        "on_submit": "sales_agent_commission.sales_agent_commission.doctype.sales_agent_commission_entry.sales_agent_commission_entry.create_commission_entries"
    }
}
```

### **Issue 10: Version Compatibility**

**Error**: `AttributeError: module 'frappe' has no attribute 'new_doc'`

**Solution**: Check ERPNext version compatibility:
```bash
# Check versions
bench version
```

**Minimum Requirements**:
- ERPNext v13.0+
- Frappe Framework v13.0+

## 🔍 **Diagnostic Commands**

### **Check App Installation**:
```bash
bench --site your-site list-apps
```

### **Check Doctype Status**:
```bash
bench --site your-site console
```
```python
import frappe
frappe.get_all("DocType", filters={"module": "Sales Agent Commission"})
```

### **Check Custom Fields**:
```bash
bench --site your-site console
```
```python
import frappe
frappe.get_all("Custom Field", filters={"dt": "Sales Partner"})
```

### **Check Permissions**:
```bash
bench --site your-site console
```
```python
import frappe
frappe.get_all("DocPerm", filters={"parent": "Sales Agent"})
```

### **Check Database Tables**:
```bash
bench --site your-site mariadb
```
```sql
SHOW TABLES LIKE '%Sales Agent%';
DESCRIBE `tabSales Agent`;
```

## 🚀 **Clean Installation Steps**

If you encounter multiple issues, try a clean installation:

### **Step 1: Remove Existing Installation**
```bash
bench --site your-site uninstall-app sales_agent_commission
```

### **Step 2: Clean App Directory**
```bash
rm -rf apps/sales_agent_commission
```

### **Step 3: Fresh Installation**
```bash
# Get app
bench get-app https://github.com/your-repo/sales_agent_commission.git

# Install app
bench --site your-site install-app sales_agent_commission

# Migrate
bench --site your-site migrate

# Restart
bench restart
```

### **Step 4: Verify Installation**
```bash
# Check app
bench --site your-site list-apps

# Check doctypes
bench --site your-site console
```
```python
import frappe
print(frappe.get_all("DocType", filters={"module": "Sales Agent Commission"}))
```

## 📋 **Installation Checklist**

- [ ] All doctype directories have `__init__.py` files
- [ ] All doctypes have both `.py` and `.json` files
- [ ] App structure follows Frappe guidelines
- [ ] Hooks.py is properly configured
- [ ] Custom fields are created
- [ ] Naming series are set up
- [ ] Permissions are configured
- [ ] Database migration completed
- [ ] Workspace is visible
- [ ] No console errors

## 🆘 **Getting Help**

If issues persist:

1. **Check Error Logs**:
   ```bash
   tail -f logs/web.error.log
   tail -f logs/worker.error.log
   ```

2. **Enable Debug Mode**:
   ```bash
   bench --site your-site set-config developer_mode 1
   ```

3. **Verbose Migration**:
   ```bash
   bench --site your-site migrate --verbose
   ```

4. **Check Console**:
   - Open browser developer tools
   - Check for JavaScript errors
   - Verify network requests

## 🔧 **Manual Fixes**

### **Create Missing __init__.py Files**:
```bash
find sales_agent_commission/doctype -type d -exec touch {}/__init__.py \;
```

### **Fix File Permissions**:
```bash
chmod -R 755 sales_agent_commission/
```

### **Rebuild Assets**:
```bash
bench build --app sales_agent_commission
```

This troubleshooting guide should resolve most installation issues. Follow the steps systematically for the best results.