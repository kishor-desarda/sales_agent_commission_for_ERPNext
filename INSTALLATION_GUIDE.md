# Sales Agent Commission System - Installation Guide

## 🚀 **Complete Installation & Setup Guide**

This guide will help you install and configure the comprehensive Sales Agent Commission system that provides industry-standard commission management with payment reconciliation.

## 📋 **Prerequisites**

- ERPNext v13.0 or higher
- Administrator access to ERPNext
- Basic understanding of ERPNext doctypes and workflows

## 🔧 **Installation Methods**

### **Method 1: Using Bench (Recommended)**

```bash
# Navigate to your ERPNext site directory
cd /path/to/your/erpnext/site

# Install the app
bench get-app https://github.com/your-repo/sales_agent_commission.git
bench --site your-site-name install-app sales_agent_commission

# Restart and migrate
bench --site your-site-name migrate
bench restart
```

### **Method 2: Manual Installation**

1. **Download the app**:
   ```bash
   cd /path/to/frappe-bench/apps
   git clone https://github.com/your-repo/sales_agent_commission.git
   ```

2. **Install the app**:
   ```bash
   bench --site your-site-name install-app sales_agent_commission
   bench --site your-site-name migrate
   ```

3. **Restart services**:
   ```bash
   bench restart
   ```

## 🏗️ **Post-Installation Setup**

### **1. Verify Installation**

1. **Check Workspace**: Go to **Selling** → Look for **Sales Commission** section
2. **Check Doctypes**: Verify these doctypes are available:
   - Sales Agent
   - Sales Agent Commission Entry
   - Commission Payment Voucher
   - Sales Agent Customer Assignment

### **2. Configure Naming Series**

Go to **Settings** → **Naming Series** and verify:
- **Sales Agent**: `AGT-.####`
- **Sales Agent Commission Entry**: `SACE-.YYYY.-`
- **Commission Payment Voucher**: `CPV-.YYYY.-`

### **3. Set Up Permissions**

The system automatically creates permissions for:
- **Sales Manager**: Full access to all documents
- **Sales User**: Read access to commission entries
- **Accounts Manager**: Access to payment vouchers

### **4. Configure Custom Fields**

The system automatically adds these custom fields:

**Sales Partner**:
- Linked Sales Agent
- Auto Create Commission Entries

**Sales Invoice**:
- Sales Agent
- Commission Entries Created

**Customer**:
- Primary Sales Agent
- Commission Applicable

## 👥 **Setting Up Your First Sales Agent**

### **Step 1: Create Sales Agent**

1. Go to **Selling** → **Sales Commission** → **Sales Agents**
2. Click **New**
3. Fill in the details:

**Basic Information**:
- **Agent Code**: Auto-generated (AGT-0001)
- **Agent Name**: Full name of the agent
- **Status**: Active
- **Joining Date**: Agent's joining date
- **Agent Type**: External/Internal/Distributor/Dealer

**Commission Structure**:
- **Commission Calculation Method**: Percentage/Fixed Amount/Tiered
- **Item Group Commission Rates**: 
  - Add rows for each item group
  - Set commission percentage for each

**Territory Allocation**:
- **Territories**: Add territories assigned to agent
- **Primary Territory**: Mark one as primary
- **Allocation Percentage**: Set percentage allocation

**Payment Details**:
- **Bank Account**: Link bank account
- **Payment Method**: Bank Transfer/Cash/Cheque
- **Payment Terms**: Net 30/Net 15, etc.

**Commission Settings**:
- **Enable Commission**: ✓ Checked
- **Commission on Payment**: ✓ Checked (Commission due only on payment)
- **Auto Create Commission Entries**: ✓ Checked

4. **Save and Submit** the document

### **Step 2: Assign Customers to Agent**

1. Go to **Sales Agent Customer Assignment**
2. Create new assignment:
   - **Sales Agent**: Select your agent
   - **Customer**: Select customer
   - **Territory**: Select territory
   - **Commission Override**: If different from agent's standard rates

### **Step 3: Test Commission Flow**

1. **Create Sales Invoice**:
   - Select customer assigned to agent
   - Add items from item groups with commission rates
   - Set **Sales Agent** field
   - Submit the invoice

2. **Verify Commission Entry**:
   - Check **Sales Agent Commission Entry** is created
   - Status should be "Pending Invoice Payment"
   - Commission amount calculated correctly

3. **Create Payment Entry**:
   - Create payment against the sales invoice
   - Submit the payment entry

4. **Verify Commission Status**:
   - Commission entry status should change to "Due for Payment"
   - Commission due amount should be calculated based on payment

## 🔄 **Understanding the Commission Flow**

### **Status Flow Diagram**:

```
Sales Invoice Submitted
         ↓
Commission Entry Created (Status: "Pending Invoice Payment")
         ↓
Payment Entry Posted
         ↓
Commission Status: "Due for Payment"
         ↓
Commission Payment Voucher Created
         ↓
Commission Status: "Paid"
```

### **Key Logic Points**:

1. **Commission Creation**: Automatic when Sales Invoice is submitted
2. **Commission Due**: Only when payment is received (not on invoice posting)
3. **Payment Reconciliation**: Commission amount based on payment percentage
4. **Agent Visibility**: Agents can see pending invoices and commission status

## 📊 **Using Reports**

### **Available Reports**:

1. **Sales Agent Commission Summary**:
   - Go to **Reports** → **Sales Agent Commission Summary**
   - Filter by agent, date range, status
   - Shows detailed commission breakdown

2. **Sales Agent Commission Payable**:
   - Shows outstanding commission amounts
   - Filter by agent, due date
   - Export for payment processing

3. **Sales Agent Performance**:
   - Agent performance metrics
   - Commission trends
   - Territory-wise analysis

### **Dashboard Features**:

1. **Sales Commission Workspace**:
   - Quick access to all commission functions
   - Real-time commission status
   - Pending payment alerts

2. **Agent Dashboard**:
   - Commission summary for each agent
   - Pending invoice tracking
   - Payment due analysis

## 🛠️ **Advanced Configuration**

### **1. Multi-Currency Setup**

For foreign currency transactions:
1. Enable multi-currency in **Accounts Settings**
2. Set up exchange rates
3. Commission will be calculated in invoice currency
4. Payment reconciliation handles currency conversion

### **2. Tiered Commission Rates**

For complex commission structures:
1. Set **Commission Calculation Method** to "Tiered"
2. Add tier rates in **Sales Agent Commission Rate** child table
3. Define amount ranges and corresponding rates

### **3. Territory-Based Rates**

For different rates by territory:
1. Create multiple **Sales Agent Commission Rate** entries
2. Set different rates for different territories
3. Use **Territory Allocation** to manage assignments

### **4. Approval Workflow**

To add approval for agents:
1. Create **Workflow** for Sales Agent doctype
2. Set approval states and transitions
3. Assign approval roles

## 🔍 **Troubleshooting**

### **Common Issues**:

1. **Sales Commission not visible in sidebar**:
   - Clear cache: `bench --site your-site clear-cache`
   - Restart: `bench restart`
   - Check workspace permissions

2. **Commission entries not created automatically**:
   - Verify Sales Agent has **Auto Create Commission Entries** enabled
   - Check if Sales Invoice has **Sales Agent** field filled
   - Verify agent status is "Active"

3. **Commission not becoming due after payment**:
   - Check if agent has **Commission on Payment** enabled
   - Verify Payment Entry is properly linked to Sales Invoice
   - Check Payment Reconciliation entries

4. **Permission issues**:
   - Verify user roles have proper permissions
   - Check if custom fields are visible to user roles

### **Debug Steps**:

1. **Check Error Logs**:
   ```bash
   bench --site your-site logs
   ```

2. **Verify Document Events**:
   - Check if hooks are properly configured
   - Verify document event handlers are working

3. **Database Consistency**:
   ```bash
   bench --site your-site console
   ```
   ```python
   frappe.db.sql("SELECT * FROM `tabSales Agent Commission Entry` LIMIT 5")
   ```

## 🔒 **Security & Permissions**

### **Default Permissions**:

- **Sales Manager**: Full access to all commission documents
- **Sales User**: Read access to commission entries
- **Accounts Manager**: Access to payment vouchers
- **System Manager**: Full system access

### **Data Security**:

- All documents have proper audit trails
- Commission calculations are logged
- Payment reconciliation is tracked
- User access is logged and monitored

## 📈 **Performance Optimization**

### **Database Optimization**:

1. **Indexes**: System creates proper indexes for performance
2. **Queries**: Optimized queries for large datasets
3. **Caching**: Proper caching for frequently accessed data

### **Scheduled Tasks**:

1. **Daily Status Update**: Updates commission status daily
2. **Weekly Statements**: Sends commission statements to agents
3. **Monthly Reconciliation**: Reconciles payment data

## 🆘 **Support & Maintenance**

### **Regular Maintenance**:

1. **Monthly**: Review commission entries and payment reconciliation
2. **Quarterly**: Audit agent performance and commission rates
3. **Annually**: Review system configuration and optimization

### **Backup Strategy**:

1. **Daily Backups**: Automatic daily backups
2. **Commission Data**: Special attention to commission calculations
3. **Audit Trails**: Preserve all audit information

### **Support Channels**:

1. **Documentation**: Comprehensive system documentation
2. **Error Logging**: Detailed error logs for troubleshooting
3. **User Training**: Training materials for users

## ✅ **Verification Checklist**

After installation, verify:

- [ ] Sales Commission workspace is visible under Selling
- [ ] All doctypes are accessible and functional
- [ ] Custom fields are added to Sales Partner, Sales Invoice, Customer
- [ ] Naming series are configured correctly
- [ ] Permissions are set up properly
- [ ] Test commission flow works end-to-end
- [ ] Reports are accessible and functional
- [ ] Email notifications are working
- [ ] Scheduled tasks are configured

## 🎯 **Next Steps**

1. **User Training**: Train your sales and accounts teams
2. **Data Migration**: Migrate existing agent data if needed
3. **Process Documentation**: Document your specific commission processes
4. **Performance Monitoring**: Set up monitoring for system performance
5. **Regular Reviews**: Schedule regular system reviews and optimizations

This comprehensive system provides industry-standard commission management with complete audit trails, payment reconciliation, and user-friendly interfaces. The system is designed to handle complex commission structures while maintaining simplicity for end users.