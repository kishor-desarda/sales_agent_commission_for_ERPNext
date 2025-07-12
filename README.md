# Sales Agent Commission Management System

A comprehensive ERPNext app for managing sales agent commissions with advanced features including foreign currency support, payment tracking, and detailed reporting.

## Features

### 🎯 Core Functionality
- **Item Group-wise Commission Rules**: Define different commission rates for different item groups per agent
- **Customer Assignment Management**: Assign customers to specific agents with priority and exclusivity options
- **Automatic Commission Calculation**: Commission entries are automatically created when Sales Invoices are submitted
- **Payment Tracking**: Track commission payments with proper reconciliation
- **Foreign Currency Support**: Full support for multi-currency transactions
- **Comprehensive Reporting**: Detailed reports for commission analysis and payable tracking

### 📊 Key Components

#### 1. Agent Commission Rule
- Define commission rules per agent and company
- Item group-wise commission rates using child tables
- Support for percentage, fixed amount, and tiered calculation methods
- Effective date ranges for rule validity
- Minimum and maximum commission limits

#### 2. Agent Customer Assignment
- Assign customers to sales agents
- Priority-based assignments
- Exclusive assignment options
- Commission rate overrides per assignment
- Date-based validity

#### 3. Agent Commission Entry
- Automatically created from Sales Invoices
- Item-wise commission breakdown
- Payment status tracking (Pending, Partially Paid, Paid, Cancelled)
- Outstanding amount calculation
- Integration with payment vouchers

#### 4. Commission Payment Voucher
- Create commission payments to agents
- Multiple payment methods support
- Link to commission entries
- Automatic status updates
- Payment reconciliation

### � System Flow

1. **Setup Phase**:
   - Create Agent Commission Rules with item group rates
   - Assign customers to agents
   - Configure company and currency settings

2. **Sales Process**:
   - Create Sales Invoice
   - System automatically creates commission entries
   - Commission calculated based on rules and assignments

3. **Payment Process**:
   - Create Commission Payment Voucher
   - Select commission entries to pay
   - System updates payment status automatically

4. **Reporting**:
   - Commission Summary Report
   - Commission Payable Report
   - Detailed analytics and charts

### 🌍 Foreign Currency Support

The system fully supports foreign currency transactions:
- Commission amounts in original currency
- Exchange rate tracking
- Company currency conversion
- Multi-currency payment vouchers

### 📈 Reporting Features

#### Agent Commission Summary
- Detailed commission entries
- Payment status tracking
- Date range filtering
- Agent and customer filtering
- Interactive charts

#### Agent Commission Payable
- Outstanding commission amounts
- Payment due tracking
- Agent-wise summaries
- Last payment date tracking

### 🎨 User Interface

#### Sidebar Integration
- Sales Commission submenu under Selling section
- Quick access to all commission-related documents
- Organized menu structure

#### Intuitive Forms
- Child tables for better data organization
- Automatic calculations
- Validation rules
- User-friendly field labels

### 🔧 Technical Features

#### Document Events
- Automatic commission entry creation on Sales Invoice submit
- Payment status updates on Payment Entry submit
- Commission entry updates on Payment Voucher submit
- Proper cancellation handling

#### Data Validation
- Payment amount validation
- Commission rate validation
- Assignment priority validation
- Currency and exchange rate validation

#### Security
- Role-based permissions
- Company-wise data isolation
- Document-level access control

## Installation

1. Install the app in your ERPNext instance
2. Run `bench migrate` to create database tables
3. Configure naming series for all doctypes
4. Set up initial commission rules and assignments

## Configuration

### 1. Naming Series
Configure naming series for:
- Agent Commission Rule: `ACR-.YYYY.-`
- Agent Commission Entry: `ACE-.YYYY.-`
- Commission Payment Voucher: `CPV-.YYYY.-`
- Agent Customer Assignment: `ACA-.YYYY.-`

### 2. Permissions
The system includes role-based permissions for:
- Sales Manager: Full access
- Sales User: Limited access
- Accounts Manager: Payment-related access

### 3. Company Setup
- Configure default company
- Set up currencies and exchange rates
- Configure item groups for commission rules

## Usage Examples

### Creating Commission Rules
1. Go to **Selling > Sales Commission > Commission Rules**
2. Create new rule for an agent
3. Add item group-wise commission rates
4. Set effective dates and limits
5. Submit the rule

### Assigning Customers
1. Go to **Selling > Sales Commission > Customer Assignments**
2. Create assignment for agent-customer pair
3. Set priority and exclusivity
4. Add commission overrides if needed
5. Submit the assignment

### Processing Payments
1. Go to **Selling > Sales Commission > Payment Vouchers**
2. Create new payment voucher
3. Select agent and commission entries
4. Enter payment details
5. Submit to update commission entries

## Reports

### Commission Summary Report
- **Path**: Selling > Sales Commission > Commission Summary
- **Purpose**: View all commission entries with filtering options
- **Features**: Date range, agent, customer, payment status filters

### Commission Payable Report
- **Path**: Selling > Sales Commission > Commission Payable
- **Purpose**: Track outstanding commission amounts
- **Features**: Agent-wise outstanding amounts, payment due tracking

## Troubleshooting

### Common Issues

1. **Commission entries not created**:
   - Check if customer is assigned to an agent
   - Verify commission rules are active and effective
   - Ensure item groups have commission rates defined

2. **Payment status not updating**:
   - Verify Payment Entry is linked to Sales Invoice
   - Check commission entry payment status
   - Ensure proper document submission

3. **Foreign currency issues**:
   - Verify exchange rates are set
   - Check currency configuration
   - Ensure proper conversion rates

### Support

For technical support and issues:
- Check ERPNext documentation
- Review system logs
- Contact development team

## Development

### Code Structure
```
sales_agent_commission/
├── doctype/
│   ├── agent_commission_rule/
│   ├── agent_commission_entry/
│   ├── commission_payment_voucher/
│   ├── agent_customer_assignment/
│   └── child_tables/
├── report/
│   ├── agent_commission_summary/
│   └── agent_commission_payable/
├── public/
│   └── js/
├── overrides.py
├── hooks.py
└── README.md
```

### Customization
The system is designed for easy customization:
- Extend commission calculation logic
- Add custom validation rules
- Create additional reports
- Modify UI components

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## Version History

- **v1.0.0**: Initial release with core functionality
- **v1.1.0**: Added foreign currency support
- **v1.2.0**: Enhanced reporting and UI improvements
- **v1.3.0**: Payment reconciliation and advanced features 