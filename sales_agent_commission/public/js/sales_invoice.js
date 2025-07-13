// Copyright (c) 2024, Sales Agent Commission and contributors
// For license information, please see license.txt

frappe.ui.form.on('Sales Invoice', {
    refresh: function(frm) {
        // Add button to view commission entries
        if (frm.doc.docstatus === 1 && frm.doc.commission_entries_created) {
            frm.add_custom_button(__('View Commission Entries'), function() {
                frappe.set_route('List', 'Agent Commission Entry', {
                    'sales_invoice': frm.doc.name
                });
            }, __('Agent Commission'));
        }
        
        // Add button to create commission entries manually if not created
        if (frm.doc.docstatus === 1 && !frm.doc.commission_entries_created) {
            frm.add_custom_button(__('Create Commission Entries'), function() {
                frappe.call({
                    method: 'sales_agent_commission.doctype.agent_commission_entry.agent_commission_entry.create_commission_from_invoice',
                    args: {
                        sales_invoice: frm.doc.name
                    },
                    callback: function(r) {
                        if (r.message && r.message.length > 0) {
                            frappe.msgprint(__('Created {0} commission entries', [r.message.length]));
                            frm.reload_doc();
                        } else {
                            frappe.msgprint(__('No applicable agents found for commission'));
                        }
                    }
                });
            }, __('Agent Commission'));
        }
        
        // Show applicable agents preview
        if (frm.doc.docstatus === 0 && frm.doc.customer && frm.doc.territory) {
            frappe.call({
                method: 'sales_agent_commission.overrides.get_applicable_agents_for_invoice',
                args: {
                    sales_invoice: frm.doc.name
                },
                callback: function(r) {
                    if (r.message && r.message.length > 0) {
                        let agent_names = r.message.map(a => a.agent_name).join(', ');
                        frm.set_df_property('applicable_agents', 'description', 
                            __('Agents eligible for commission: {0}', [agent_names]));
                    }
                }
            });
        }
    },
    
    customer: function(frm) {
        // Update applicable agents when customer changes
        if (frm.doc.customer && frm.doc.territory) {
            frm.trigger('refresh');
        }
    },
    
    territory: function(frm) {
        // Update applicable agents when territory changes
        if (frm.doc.customer && frm.doc.territory) {
            frm.trigger('refresh');
        }
    }
});