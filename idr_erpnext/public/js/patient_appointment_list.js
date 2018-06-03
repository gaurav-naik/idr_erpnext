frappe.listview_settings['Patient Appointment'] = {
	onload: function(listview) {
		var method = "idr_erpnext.api.create_doctor_invoices";

		listview.page.add_menu_item(__("Create Doctor Invoice"), function() {
			var d = new frappe.ui.Dialog({
				title: __("Create Doctor Invoice"),
				fields: [
					{ fieldtype: 'Link', fieldname: 'physician', label: __("Physician"), options:'Physician'},
					{ fieldtype: 'Date', fieldname: 'date', label: __("Date")},
				],
				primary_action_label: __("Create"),
				primary_action: function() {
					frappe.call({
						method: method,
						args: {
							filters: d.get_values()
						}
					}).done(function(r) {
						d.hide();
					}).error(function(err) {
						frappe.show_alert(__("Could not create invoices."));
						d.hide();
					});
				}
			});
			d.show();
		});
	}
}