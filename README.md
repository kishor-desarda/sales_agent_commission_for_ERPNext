# 🎯 Sales Agent Commission App

A comprehensive Sales Agent Commission Management System for ERPNext.

## 📋 **Features**

- **Agent Commission Rules**: Define commission structures and rates
- **Commission Entries**: Track and calculate agent commissions
- **Customer Assignments**: Assign customers to specific agents
- **Payment Vouchers**: Generate commission payment vouchers
- **Commission Reports**: Detailed commission summaries and reports

## 🚀 **Installation**

### **Using Bench (Recommended)**
```bash
bench get-app https://github.com/your-username/sales_agent_commission.git
bench --site your-site.com install-app sales_agent_commission
```

### **Manual Installation**
1. Clone this repository to your `apps` directory
2. Run: `bench --site your-site.com install-app sales_agent_commission`

## 📦 **App Structure**

```
sales_agent_commission/
├── __init__.py                    # App version
├── hooks.py                       # App configuration & events
├── modules.txt                    # Module definition
├── pyproject.toml                 # Package configuration
└── sales_agent_commission/        # Main module
    ├── __init__.py
    ├── doctype/                   # Document types
    │   ├── agent_commission_entry/
    │   ├── agent_commission_rule/
    │   ├── agent_customer_assignment/
    │   ├── commission_payment_voucher/
    │   └── commission_payment_item/
    └── report/                    # Reports
        └── agent_commission_summary/
```

## 🔧 **Configuration**

After installation, configure the app through:
- **Agent Commission Rules**: Set up commission structures
- **Customer Assignments**: Assign customers to agents
- **Commission Settings**: Configure default rates and policies

## 📊 **Usage**

1. **Create Commission Rules**: Define how commissions are calculated
2. **Assign Customers**: Link customers to sales agents
3. **Generate Entries**: Create commission entries for sales
4. **Process Payments**: Generate payment vouchers for agents
5. **View Reports**: Monitor commission summaries and trends

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 **License**

MIT License - see LICENSE file for details.

## 🆘 **Support**

For support and questions, please open an issue on GitHub. 