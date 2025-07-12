# Sales Agent Commission App - Installation Guide

## Prerequisites

- ERPNext version 15.0.0 or higher
- Frappe Framework version 15.0.0 or higher
- Python 3.10 or higher

## Installation Methods

### Method 1: Using Bench (Recommended)

1. **Navigate to your ERPNext apps directory:**
   ```bash
   cd /path/to/your/erpnext-bench/apps
   ```

2. **Clone the repository:**
   ```bash
   bench get-app https://github.com/your-username/sales_agent_commission.git
   ```

3. **Install the app:**
   ```bash
   bench --site your-site.com install-app sales_agent_commission
   ```

4. **Run migrations:**
   ```bash
   bench --site your-site.com migrate
   ```

5. **Build assets:**
   ```bash
   bench build
   ```

### Method 2: Manual Installation

1. **Download the app:**
   ```bash
   git clone https://github.com/your-username/sales_agent_commission.git
   cd sales_agent_commission
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Copy to ERPNext apps directory:**
   ```bash
   cp -r sales_agent_commission /path/to/your/erpnext-bench/apps/
   ```

4. **Install the app:**
   ```bash
   bench --site your-site.com install-app sales_agent_commission
   ```

5. **Run migrations:**
   ```bash
   bench --site your-site.com migrate
   ```

6. **Build assets:**
   ```bash
   bench build
   ```

### Method 3: Using pip

1. **Install via pip:**
   ```bash
   pip install sales_agent_commission
   ```

2. **Add to ERPNext apps:**
   ```bash
   bench --site your-site.com install-app sales_agent_commission
   ```

3. **Run migrations:**
   ```bash
   bench --site your-site.com migrate
   ```

## Post-Installation Setup

### 1. Configure Naming Series

The app will automatically create the following naming series:
- `ACR-.YYYY.-` for Agent Commission Rules
- `ACE-.YYYY.-` for Agent Commission Entries
- `CPV-.YYYY.-` for Commission Payment Vouchers
- `ACA-.YYYY.-` for Agent Customer Assignments

### 2. Set Up Permissions

The app creates default permissions for the following roles:
- **Sales Manager**: Full access to all commission features
- **Sales User**: Limited access to view and create
- **Accounts Manager**: Payment-related access

### 3. Configure Company Settings

1. Go to **Setup > Company**
2. Select your company
3. Ensure the default currency is set correctly
4. Configure item groups for commission rules

### 4. Create Initial Data

#### Create Item Groups
1. Go to **Stock > Item Group**
2. Create item groups for different product categories
3. These will be used in commission rules

#### Create Sales Partners (Agents)
1. Go to **CRM > Sales Partner**
2. Create sales partners who will receive commissions
3. Set their commission rates and details

## Verification

### 1. Check Installation

1. Go to **Setup > Apps**
2. Verify that "Sales Agent Commission" is listed and active

### 2. Check Menu Integration

1. Go to **Selling** in the sidebar
2. You should see a "Sales Commission" submenu with:
   - Commission Rules
   - Customer Assignments
   - Commission Entries
   - Payment Vouchers
   - Commission Summary
   - Commission Payable

### 3. Test Basic Functionality

1. **Create a Commission Rule:**
   - Go to **Selling > Sales Commission > Commission Rules**
   - Create a new rule for an agent
   - Add item group-wise commission rates

2. **Assign a Customer:**
   - Go to **Selling > Sales Commission > Customer Assignments**
   - Create an assignment linking a customer to an agent

3. **Test Commission Creation:**
   - Create a Sales Invoice for the assigned customer
   - Check if commission entries are automatically created

## Troubleshooting

### Common Issues

#### 1. App Not Appearing in Menu
- **Solution**: Clear browser cache and refresh
- **Solution**: Restart the Frappe server
- **Solution**: Check if the app is properly installed

#### 2. Commission Entries Not Created
- **Check**: Customer is assigned to an agent
- **Check**: Commission rules are active and effective
- **Check**: Item groups have commission rates defined

#### 3. Permission Errors
- **Solution**: Check user roles and permissions
- **Solution**: Ensure user has access to the company
- **Solution**: Verify custom permissions are created

#### 4. Naming Series Errors
- **Solution**: Check if naming series exist in the system
- **Solution**: Reinstall the app to recreate naming series

### Debug Mode

To enable debug mode for troubleshooting:

1. **Enable debug in site config:**
   ```bash
   bench --site your-site.com set-config -g debug 1
   ```

2. **Check logs:**
   ```bash
   bench --site your-site.com tail-logs
   ```

3. **Check error logs:**
   ```bash
   bench --site your-site.com tail-logs error
   ```

## Upgrading

### Upgrade Process

1. **Backup your data:**
   ```bash
   bench --site your-site.com backup
   ```

2. **Update the app:**
   ```bash
   cd /path/to/your/erpnext-bench/apps/sales_agent_commission
   git pull origin main
   ```

3. **Run migrations:**
   ```bash
   bench --site your-site.com migrate
   ```

4. **Build assets:**
   ```bash
   bench build
   ```

5. **Restart services:**
   ```bash
   bench restart
   ```

### Version Compatibility

| App Version | ERPNext Version | Frappe Version |
|-------------|----------------|----------------|
| 1.0.0       | 15.0.0+        | 15.0.0+        |

## Uninstallation

### Remove the App

1. **Uninstall the app:**
   ```bash
   bench --site your-site.com uninstall-app sales_agent_commission
   ```

2. **Remove from apps directory:**
   ```bash
   rm -rf /path/to/your/erpnext-bench/apps/sales_agent_commission
   ```

3. **Clean up database (optional):**
   ```bash
   bench --site your-site.com drop-database
   bench --site your-site.com new-database
   ```

### Data Backup

Before uninstalling, backup your commission data:

1. **Export commission data:**
   ```bash
   bench --site your-site.com export-doc Agent Commission Rule
   bench --site your-site.com export-doc Agent Commission Entry
   bench --site your-site.com export-doc Commission Payment Voucher
   bench --site your-site.com export-doc Agent Customer Assignment
   ```

## Support

### Getting Help

1. **Documentation**: Check the README.md file
2. **Issues**: Report bugs on GitHub
3. **Community**: Ask questions in ERPNext community forums
4. **Email**: Contact support@frappe.io

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This app is licensed under the MIT License. See the LICENSE file for details.