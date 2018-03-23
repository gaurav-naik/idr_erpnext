frappe.ui.form.on("Sales Invoice", {
	"onload_post_render": function(frm) {
		//Scroll directly to items if Invoice has been opened from Patient doctype.
		var last_route = frappe.route_history.slice(-2, -1)[0];
		if (last_route && last_route[0] == "Form" && last_route[1] == "Patient Appointment") {

			frappe.call({
				method: "idr_erpnext.api.get_procedure_data_from_appointment",
				args: {
					patient_appointment: cur_frm.doc.appointment
				}
			}).done(function(r) {
				var first_item = locals["Sales Invoice Item"][cur_frm.doc.items[0].name];
				first_item.item_code = r.message.idr_appointment_type;
				first_item.item_name = r.message.idr_appointment_type;
				first_item.description = r.message.idr_appointment_type;
				first_item.rate = r.message.rate;
				first_item.qty = 1;
				first_item.amount = first_item.rate * first_item.qty;

				refresh_field("items");
			});
		}
	}
});