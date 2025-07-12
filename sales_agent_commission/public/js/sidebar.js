// Add Sales Commission submenu under Selling
frappe.provide('frappe.ui');

frappe.ui.Sidebar.prototype.add_sales_commission_menu = function() {
	// Find the Selling menu
	const selling_menu = this.find('.sidebar-menu a[href="#modules/Selling"]');
	if (selling_menu.length) {
		const selling_li = selling_menu.closest('li');
		
		// Check if Sales Commission submenu already exists
		if (!selling_li.find('.sales-commission-submenu').length) {
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
			selling_li.append(submenu);
			
			// Add click handler to toggle submenu
			selling_menu.on('click', function(e) {
				e.preventDefault();
				const submenu = $(this).siblings('.sales-commission-submenu');
				submenu.slideToggle();
			});
		}
	}
};

// Initialize sidebar menu when page loads
$(document).ready(function() {
	if (frappe.ui.Sidebar) {
		const sidebar = new frappe.ui.Sidebar();
		sidebar.add_sales_commission_menu();
	}
});

// Also initialize when sidebar is refreshed
frappe.after_ajax(function() {
	if (frappe.ui.Sidebar) {
		const sidebar = new frappe.ui.Sidebar();
		sidebar.add_sales_commission_menu();
	}
});