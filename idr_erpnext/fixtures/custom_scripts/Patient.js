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
	"idr_patient_first_name": function(frm) {
		make_full_name(frm);
	},
	"idr_patient_last_name": function (frm) {
		make_full_name(frm);
	},
	"idr_patient_phone_no": function(frm) {
		frm.set_value("phone", frm.doc.idr_patient_phone_no);
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
