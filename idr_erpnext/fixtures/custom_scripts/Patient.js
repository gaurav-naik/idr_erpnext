frappe.ui.form.on("Patient", {
	"onload": function(frm) {
		//Filter addresses by customer.
		frm.set_query("idr_patient_address", function() {
			return {
				"query": "frappe.contacts.doctype.address.address.address_query",
				"filters": {
					"link_doctype":"Customer",
					"link_name":frm.doc.customer
				}
			};
		});
	},
	"idr_patient_address": function(frm) {
		set_patient_address(frm);
	},
	"customer": function(frm) {
		if (frm.doc.customer === undefined) {
			frm.set_value("idr_patient_address", undefined);
		}
	},
	"refresh": function(frm) {
		add_custom_buttons(frm);
	},
	"idr_patient_first_name": function(frm) {
		make_full_name(frm);
	},
	"idr_patient_last_name": function (frm) {
		make_full_name(frm);
	},
	"idr_patient_phone_no": function(frm) {
		frm.set_value("phone", idr_patient_phone);
	}
});

function make_full_name(frm) {
	frm.set_value("patient_name", [frm.doc.idr_patient_first_name, frm.doc.idr_patient_last_name].join(" ").trim());
}

function set_patient_address(frm) {
	if (frm.doc.idr_patient_address) {
		frappe.call({
			method: "idr_erpnext.api.get_patient_address_display",
			args: {
				"address_name": frm.doc.idr_patient_address,
			}
		}).done(function(r) {
			frm.set_value("idr_patient_address_display", r.message);
		});
	} else {
		frm.set_value("idr_patient_address_display", undefined);
	}
}

function add_custom_buttons(frm) {
	if (!frm.doc.__islocal) {
		frm.add_custom_button(__('Sales Invoice'), function() {
			make_sales_invoice(frm);
		},__("Create"));
	}

	if (!(__("Generate Codice Fiscale") in frm.custom_buttons)) {
		frm.add_custom_button(__("Generate Codice Fiscale"), function() {
			if (!frm.doc.sex) {
				frappe.msgprint(__("Gender is required for generating Codice Fiscale"));
			} else if (!frm.doc.idr_place_of_birth) {
				frappe.msgprint(__("Place of birth is required for generating Codice Fiscale"));
			} else {
				frappe.call({
					method:"idr_erpnext.api.generate_codice_fiscale",
					args: {
						"first_name":frm.doc.idr_patient_first_name,
						"last_name":frm.doc.idr_patient_last_name,
						"gender": frm.doc.sex,
						"date_of_birth": frm.doc.dob,
						"place_of_birth": frm.doc.idr_place_of_birth
					}
				}).done(function(r) {
					if (!r.exc) {
						frm.set_value("idr_patient_codice_fiscale", r.message);
					}
				});
			}
		});
	}
}

// Discontinued after using Patient Appointment flow
// function make_sales_invoice(frm) {
// 	frappe.call({
// 		method: "idr_erpnext.api.create_invoice_for_patient",
// 		args: {
// 			patient_customer: frm.doc.customer
// 		},
// 		freeze: true,
// 		freeze_message: __("Creating Sales Invoice...")
// 	}).done((r) => {
// 		if (!r.exc) {
// 			frappe.model.sync(r.message);
// 			frappe.set_route("Form", r.message.doctype, r.message.name);
// 		} else {
// 			frappe.show_alert(__("Unable to create Sales Invoice. <br>") + r.exc);
// 		}
// 	}).fail((f) => {
// 		frappe.show_alert(__("A problem occurred while creating a Sales Invoice. <br>") + f);
// 	})
// }