frappe.ui.form.on("Sales Invoice", {
	"onload_post_render": function(frm) {
		//Scroll directly to items if Invoice has been opened from Patient doctype.
		var last_route = frappe.route_history.slice(-2, -1)[0];
		if (last_route && last_route[0] == "Form" && last_route[1] == "Patient") {
			frappe.model.add_child(cur_frm.doc, "Sales Invoice Item", "items", 0);
			refresh_field("items");
 			frappe.ui.scroll("[data-fieldname='currency']", true);
		} else if (last_route && last_route[0] == "Form" && last_route[1] == "Patient Appointment") {
			frappe.db.get_value("Patient Appointment", cur_frm.doc.appointment, "idr_appointment_type", function(r) {
				let first_item = locals["Sales Invoice Item"][cur_frm.doc.items[0].name]
				first_item.item_code = r.idr_appointment_type
				first_item.item_name = r.idr_appointment_type;
				first_item.description = r.idr_appointment_type
				refresh_field("items");
			})
		}
	}
})