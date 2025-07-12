// Sales Agent Commission App JavaScript

frappe.provide('sales_agent_commission');

// Initialize app when page loads
$(document).ready(function() {
    sales_agent_commission.init();
});

sales_agent_commission.init = function() {
    // Add Sales Commission menu to sidebar
    sales_agent_commission.addSidebarMenu();
    
    // Initialize commission calculators
    sales_agent_commission.initCommissionCalculators();
    
    // Initialize payment status indicators
    sales_agent_commission.initPaymentStatus();
};

// Add Sales Commission menu to sidebar
sales_agent_commission.addSidebarMenu = function() {
    // Find the Selling menu in sidebar
    const sellingMenu = $('.sidebar-menu a[href="#modules/Selling"]');
    if (sellingMenu.length) {
        const sellingLi = sellingMenu.closest('li');
        
        // Check if Sales Commission submenu already exists
        if (!sellingLi.find('.sales-commission-submenu').length) {
            // Create Sales Commission submenu
            const submenu = $(`
                <ul class="sales-commission-submenu" style="display: none;">
                    <li>
                        <a href="#List/Agent Commission Rule" class="sidebar-item">
                            <span class="sidebar-label">Commission Rules</span>
                        </a>
                    </li>
                    <li>
                        <a href="#List/Agent Customer Assignment" class="sidebar-item">
                            <span class="sidebar-label">Customer Assignments</span>
                        </a>
                    </li>
                    <li>
                        <a href="#List/Agent Commission Entry" class="sidebar-item">
                            <span class="sidebar-label">Commission Entries</span>
                        </a>
                    </li>
                    <li>
                        <a href="#List/Commission Payment Voucher" class="sidebar-item">
                            <span class="sidebar-label">Payment Vouchers</span>
                        </a>
                    </li>
                    <li class="divider"></li>
                    <li>
                        <a href="#Report/Agent Commission Summary" class="sidebar-item">
                            <span class="sidebar-label">Commission Summary</span>
                        </a>
                    </li>
                    <li>
                        <a href="#Report/Agent Commission Payable" class="sidebar-item">
                            <span class="sidebar-label">Commission Payable</span>
                        </a>
                    </li>
                </ul>
            `);
            
            // Add submenu to Selling menu
            sellingLi.append(submenu);
            
            // Add click handler to toggle submenu
            sellingMenu.on('click', function(e) {
                e.preventDefault();
                const submenu = $(this).siblings('.sales-commission-submenu');
                submenu.slideToggle();
            });
        }
    }
};

// Initialize commission calculators
sales_agent_commission.initCommissionCalculators = function() {
    // Commission calculation for Agent Commission Rule
    if (frappe.get_route()[1] === 'Agent Commission Rule') {
        sales_agent_commission.initCommissionRuleCalculator();
    }
    
    // Commission calculation for Agent Commission Entry
    if (frappe.get_route()[1] === 'Agent Commission Entry') {
        sales_agent_commission.initCommissionEntryCalculator();
    }
};

// Initialize commission rule calculator
sales_agent_commission.initCommissionRuleCalculator = function() {
    const doc = frappe.get_doc('Agent Commission Rule');
    if (doc) {
        // Watch for changes in commission rates
        doc.commission_rates.on('change', function() {
            sales_agent_commission.calculateCommissionRule();
        });
        
        // Watch for changes in calculation method
        doc.calculation_method.on('change', function() {
            sales_agent_commission.updateCalculationMethod();
        });
    }
};

// Calculate commission rule totals
sales_agent_commission.calculateCommissionRule = function() {
    const doc = frappe.get_doc('Agent Commission Rule');
    if (!doc) return;
    
    let totalCommission = 0;
    let itemGroups = [];
    
    // Calculate totals from commission rates
    doc.commission_rates.forEach(function(rate) {
        if (rate.item_group) {
            itemGroups.push(rate.item_group);
            
            if (doc.calculation_method === 'Percentage' && rate.commission_percentage) {
                totalCommission += parseFloat(rate.commission_percentage);
            } else if (doc.calculation_method === 'Fixed Amount' && rate.fixed_amount) {
                totalCommission += parseFloat(rate.fixed_amount);
            }
        }
    });
    
    // Update summary if element exists
    const summaryElement = $('.commission-summary');
    if (summaryElement.length) {
        summaryElement.html(`
            <div class="commission-summary-widget">
                <div class="widget-title">Commission Summary</div>
                <div class="widget-value">${itemGroups.length} Item Groups</div>
                <div class="widget-label">Total Commission: ${totalCommission.toFixed(2)}</div>
            </div>
        `);
    }
};

// Update calculation method display
sales_agent_commission.updateCalculationMethod = function() {
    const doc = frappe.get_doc('Agent Commission Rule');
    if (!doc) return;
    
    const method = doc.calculation_method;
    
    // Show/hide fields based on calculation method
    if (method === 'Percentage') {
        $('.commission-percentage-field').show();
        $('.fixed-amount-field').hide();
        $('.tiered-rates-field').hide();
    } else if (method === 'Fixed Amount') {
        $('.commission-percentage-field').hide();
        $('.fixed-amount-field').show();
        $('.tiered-rates-field').hide();
    } else if (method === 'Tiered') {
        $('.commission-percentage-field').hide();
        $('.fixed-amount-field').hide();
        $('.tiered-rates-field').show();
    }
};

// Initialize commission entry calculator
sales_agent_commission.initCommissionEntryCalculator = function() {
    const doc = frappe.get_doc('Agent Commission Entry');
    if (doc) {
        // Watch for changes in commission items
        doc.commission_items.on('change', function() {
            sales_agent_commission.calculateCommissionEntry();
        });
    }
};

// Calculate commission entry totals
sales_agent_commission.calculateCommissionEntry = function() {
    const doc = frappe.get_doc('Agent Commission Entry');
    if (!doc) return;
    
    let totalCommission = 0;
    let totalBaseAmount = 0;
    
    // Calculate totals from commission items
    doc.commission_items.forEach(function(item) {
        if (item.commission_amount) {
            totalCommission += parseFloat(item.commission_amount);
        }
        if (item.base_amount) {
            totalBaseAmount += parseFloat(item.base_amount);
        }
    });
    
    // Update total commission amount
    if (doc.total_commission_amount !== totalCommission) {
        doc.total_commission_amount = totalCommission;
        doc.calculate_outstanding_amount();
        doc.refresh_field('total_commission_amount');
        doc.refresh_field('outstanding_amount');
    }
};

// Initialize payment status indicators
sales_agent_commission.initPaymentStatus = function() {
    // Add payment status styling
    $('.payment-status').each(function() {
        const status = $(this).text().trim();
        const element = $(this);
        
        element.removeClass('payment-status-pending payment-status-paid payment-status-partially-paid payment-status-cancelled');
        
        switch (status.toLowerCase()) {
            case 'pending':
                element.addClass('payment-status-pending');
                break;
            case 'paid':
                element.addClass('payment-status-paid');
                break;
            case 'partially paid':
                element.addClass('payment-status-partially-paid');
                break;
            case 'cancelled':
                element.addClass('payment-status-cancelled');
                break;
        }
    });
};

// Commission Payment Voucher functions
sales_agent_commission.initPaymentVoucher = function() {
    const doc = frappe.get_doc('Commission Payment Voucher');
    if (doc) {
        // Watch for changes in commission entries
        doc.commission_entries.on('change', function() {
            sales_agent_commission.calculatePaymentVoucher();
        });
    }
};

// Calculate payment voucher totals
sales_agent_commission.calculatePaymentVoucher = function() {
    const doc = frappe.get_doc('Commission Payment Voucher');
    if (!doc) return;
    
    let totalAmount = 0;
    
    // Calculate total from commission entries
    doc.commission_entries.forEach(function(entry) {
        if (entry.paid_amount) {
            totalAmount += parseFloat(entry.paid_amount);
        }
    });
    
    // Update total commission amount
    if (doc.total_commission_amount !== totalAmount) {
        doc.total_commission_amount = totalAmount;
        doc.refresh_field('total_commission_amount');
    }
};

// Get pending commission entries for agent
sales_agent_commission.getPendingEntries = function(agent, company) {
    return frappe.call({
        method: 'sales_agent_commission.sales_agent_commission.doctype.commission_payment_voucher.commission_payment_voucher.get_pending_commission_entries',
        args: {
            agent: agent,
            company: company
        }
    });
};

// Initialize when page loads
frappe.after_ajax(function() {
    sales_agent_commission.init();
});

// Export functions for use in other modules
window.sales_agent_commission = sales_agent_commission;