frappe.listview_settings['Patient Appointment'] = {
	onload: function(listview) {
		var method = "idr_erpnext.api.create_doctor_invoices";

		listview.page.add_menu_item(__("Create Doctor Invoice"), function() {
			listview.call_for_selected_items(method, {"filters": listview.list_renderer.filters });
		});
	}
}