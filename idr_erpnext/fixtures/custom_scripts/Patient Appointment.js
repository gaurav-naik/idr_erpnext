frappe.ui.form.on("Patient Appointment", {
	patient: function(frm) {
		frappe.call({
			method: "idr_erpnext.api.get_earliest_available_physician"// get_physician_with_earliest_timeslot"
		}).done(function(r) {
			if (!r.exc) {
				frm.set_value("physician", r.earliest_available_physician);
			}
		}).error(function(err) {
			frappe.show_alert(__("Could not fetch earliest available date."));
		});
	},
	physician: function(frm) {
		frappe.call({
			method: "idr_erpnext.api.get_earliest_available_date",
			args: {
				"physician": frm.doc.physician
			}
		}).done(function(r) {
			if (!r.exc) {
				frm.set_value("appointment_date", r.earliest_available_date);
			}
		}).error(function(err) {
			frappe.show_alert(__("Could not fetch earliest available date."));
		});
	}
});

frappe.ui.keys.on("alt+c", function(e) {
	frappe.click_button("Check availability");
});
