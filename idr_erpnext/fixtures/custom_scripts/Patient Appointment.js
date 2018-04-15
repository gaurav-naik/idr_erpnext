frappe.ui.form.on("Patient Appointment", {
	refresh: function(frm) {
		if (frm.doc.sales_invoice) {
			frm.add_custom_button(__("Delete Linked Invoice"), function() {
				frappe.call({
					method:"idr_erpnext.api.unlink_and_delete_sales_invoice",
					args: {
						patient_appointment: frm.doc.name
					},
					freeze: true,
					freeze_message: __("Deleting linked invoice...")
				}).done(function(r) {
					frm.reload_doc();
				}).error(function(r) {
					frappe.show_alert(__("Cannot unlink sales invoice"));
				});
			});
		}
	},
	patient: function(frm) {
		if (!frm.doc.patient) { return 0; }
		frappe.call({
			method: "idr_erpnext.api.get_earliest_available_physician_and_date"// get_physician_with_earliest_timeslot"
		}).done(function(r) {
			if (!r.exc) {
				frm.set_value("physician", r.message.physician);
			}
		}).error(function(err) {
			frappe.show_alert(__("Could not fetch earliest available doctor."));
		});
	},
	physician: function(frm) {
		if (!frm.doc.physician) { return 0; }
		frappe.call({
			method: "idr_erpnext.api.get_earliest_available_date",
			args: {
				"physician": frm.doc.physician
			}
		}).done(function(r) {
			if (!r.exc) {
				frm.set_value("appointment_date", r.message);
			}
		}).error(function(err) {
			console.log(err);
			frappe.show_alert(__("Could not fetch earliest available date."));
		});
	}
});

frappe.ui.keys.on("alt+c", function(e) {
	frappe.click_button("Check availability");
});
