frappe.ui.form.on("Patient Appointment", {
	onload: function(frm) {
		//Check if patient info is filled
		check_patient_details(frm);
	},
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

		//Check if patient info is filled
		check_patient_details(frm);
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
		check_patient_details(frm);
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
			frappe.show_alert(__("Could not fetch earliest available date."));
		});
	},
	appointment_date: function(frm) {
		if (frm.doc.appointment_date) {
			check_patient_details(frm);
		}
	}
});

frappe.ui.keys.on("alt+c", function(e) {
	frappe.click_button("Check availability");
});

function check_patient_details(frm) {
	if (frm.doc.patient) {
		frappe.call({
			method: "idr_erpnext.api.check_patient_details",
			args: {
				patient: frm.doc.patient,
			}
		}).done(function(r) {
			console.log(r);
			if (r && r.message && r.message.missing_details && r.message.missing_details.length > 0) {
				frm.set_df_property("patient", "label", 
					__("Patient") + '<a class="badge" style="color:white;background-color:red" href="/desk#Form/Customer/' + r.message.patient_customer + '">' 
					+ __("Customer information missing!") + '</a>'
				);
				$("button[data-doctype='Sales Invoice'].btn-new").attr('disabled', 'disabled');

				if (cur_frm.custom_buttons["Invoice"]) {
					cur_frm.custom_buttons["Invoice"].hide();
				}
			} else {
				frm.set_df_property("patient", "label", __("Patient"));
				$("button[data-doctype='Sales Invoice'].btn-new").removeAttr('disabled');

				if (cur_frm.custom_buttons["Invoice"]) {
					cur_frm.custom_buttons["Invoice"].show();
				}
			}
		}).error(function(err) {
			frappe.show_alert(__("Could not check patient details"));
		});
	}
}