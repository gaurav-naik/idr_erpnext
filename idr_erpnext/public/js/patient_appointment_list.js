frappe.listview_settings['Patient Appointment'] = {
	onload: function(listview) {
		var method = "idr_erpnext.api.create_doctor_invoices";

		listview.page.add_menu_item(__("Create Doctor Invoice"), function() {
			if (listview.get_checked_items().length) {
				listview.call_for_selected_items(method, {"filters": listview.list_renderer.filters });
			} else {
				frappe.msgprint({"message":__("Please select at least one Patient Appointment"), "title":__("Alert"), "indicator":"red"});
			}
		});
	}
}