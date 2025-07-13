# Agent Commission Management Module for ERPNext

## Overview

The Agent Commission Management module is a comprehensive solution designed to streamline and automate the entire agent commission lifecycle in ERPNext. This module provides a complete ecosystem for managing sales agents, their commission structures, and payment workflows.

## Key Features

### 1. **Single Window Agent Onboarding**
- Complete agent profile management in one place
- Contact details and multiple bank accounts
- Territory and customer assignments
- Agreement management with document upload
- Automatic agent code generation
- Ledger account creation upon submission

### 2. **Flexible Commission Structure**
- Item group-wise commission rates
- Territory-specific commission rates
- Customer-specific commission rates
- Min/max order value conditions
- Multiple commission tiers support

### 3. **Automated Commission Calculation**
- Automatic commission entry creation on Sales Invoice submission
- Ex-works value calculation (excluding freight and logistics)
- Support for both Domestic and Export invoices
- Item group-wise commission breakdown
- Multiple agents per invoice support

### 4. **Payment Workflow Integration**
- Commission status tracking (Pending → Due → Paid)
- Integration with Payment Reconciliation
- Commission becomes due only after invoice payment
- Batch payment processing
- Payment entry creation with bank details

### 5. **Comprehensive Reporting**
- Agent Commission Analytics Report with filters
- Real-time dashboards and summaries
- Monthly commission reports
- Agent-wise, territory-wise, customer-wise analytics
- Export capabilities

## Module Components

### DocTypes

1. **Agent Master**
   - Central repository for all agent information
   - Manages agent lifecycle from onboarding to deactivation

2. **Agent Commission Entry**
   - Automatically created from Sales Invoice
   - Tracks commission amount and payment status
   - Links to invoice and payment references

3. **Agent Ledger Entry**
   - Maintains running balance for each agent
   - Records all commission and payment transactions

4. **Agent Commission Payment**
   - Processes batch payments for due commissions
   - Creates accounting entries
   - Updates commission status

### Child Tables
- Agent Commission Rate
- Agent Territory Assignment
- Agent Customer Assignment
- Agent Bank Account
- Agent Commission Detail
- Agent Payment Entry Item

### Reports
- Agent Commission Analytics (comprehensive report with multiple filters)

### Scheduled Tasks
- Daily: Check agreement expiry, update commission status
- Weekly: Send commission statements to agents
- Monthly: Generate commission summary reports

## Business Process Flow

### 1. Agent Onboarding
```
Create Agent Master → Define Commission Rates → Assign Territories/Customers → Submit → Ledger Account Created
```

### 2. Commission Generation
```
Sales Invoice Created → On Submit → Check Applicable Agents → Calculate Commission → Create Commission Entries
```

### 3. Payment Process
```
Invoice Payment Received → Payment Reconciliation → Commission Status: Due → Create Payment Batch → Process Payment
```

## Key Business Rules

1. **Commission Calculation**
   - Based on Ex-works value only
   - Freight and logistics charges excluded
   - Item group-wise rates applied
   - Customer/Territory specific rates take precedence

2. **Payment Due Conditions**
   - Commission payable only after invoice payment
   - Automatic status updates through integration
   - Batch processing for efficiency

3. **Agent Status Management**
   - Active/Inactive/Suspended status tracking
   - Agreement expiry monitoring
   - Automatic notifications

## User Interface Features

1. **Intuitive Forms**
   - Section-wise organization
   - Conditional field visibility
   - Auto-fetch functionality
   - Validation messages

2. **Quick Actions**
   - View commission entries from Sales Invoice
   - Create commission entries manually
   - Process batch payments
   - Generate reports

3. **Real-time Updates**
   - Commission status tracking
   - Payment notifications
   - Agreement expiry alerts

## Integration Points

1. **Sales Invoice**
   - Custom fields for commission tracking
   - Automatic commission calculation
   - Commission entry creation

2. **Payment Reconciliation**
   - Status update triggers
   - Commission due notifications

3. **Payment Entry**
   - Commission payment tracking
   - Ledger updates

## Security and Permissions

- Role-based access control
- Sales Manager: Full access
- Sales User: Read-only access to reports
- Accounts Manager: Payment processing rights

## Benefits

1. **Automation**
   - Eliminates manual commission calculations
   - Reduces errors and disputes
   - Saves processing time

2. **Transparency**
   - Clear commission tracking
   - Agent self-service capabilities
   - Audit trail maintenance

3. **Scalability**
   - Handles multiple agents and territories
   - Supports complex commission structures
   - Efficient batch processing

4. **Compliance**
   - Agreement tracking
   - Payment documentation
   - Financial reconciliation

## Getting Started

1. **Initial Setup**
   - Configure Item Groups
   - Set up Territories
   - Define commission structures

2. **Agent Onboarding**
   - Create Agent Master records
   - Upload agreements
   - Define commission rates

3. **Operations**
   - Process Sales Invoices normally
   - Monitor commission entries
   - Process payments periodically

4. **Reporting**
   - Use Analytics Report for insights
   - Schedule automated reports
   - Monitor agent performance

## Support and Maintenance

- Regular agreement expiry checks
- Monthly reconciliation recommended
- Periodic commission rate reviews
- System performance monitoring

This module transforms agent commission management from a manual, error-prone process to an automated, transparent, and efficient system that scales with your business.