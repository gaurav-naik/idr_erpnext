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
		set_patient_address(frm)		
	},
	"customer": function(frm) {
		if (frm.doc.customer == undefined) {
			frm.set_value("idr_patient_address", undefined)
		}
	},
	"refresh": function(frm) {
		add_custom_buttons(frm);
	}
})

frappe.ui.keys.on('ctrl+i', function(e) {
	if ((cur_frm.doc.doctype == "Patient") && (!cur_frm.doc.__islocal)) {
		make_sales_invoice(cur_frm);
	}
});

function set_patient_address(frm) {
	if (frm.doc.idr_patient_address) {
		frappe.call({
			method: "idr_erpnext.api.get_patient_address_display",
			args: {
				"address_name": frm.doc.idr_patient_address,
			}
		}).done(r => {
			frm.set_value("idr_patient_address_display", r.message)
		})
	} else {
		frm.set_value("idr_patient_address_display", undefined)
	}
}

function add_custom_buttons(frm) {
	if (!frm.doc.__islocal) {
		frm.add_custom_button(__('Sales Invoice'), function() {
			make_sales_invoice(frm)
		},__("Create"));
	}
}


function make_sales_invoice(frm) {
	frappe.call({
		method: "idr_erpnext.api.create_invoice_for_patient",
		args: {
			patient_customer: frm.doc.customer
		},
		freeze: true,
		freeze_message: __("Creating Sales Invoice...")
	}).done((r) => {
		if (!r.exc) {
			frappe.model.sync(r.message);
			frappe.set_route("Form", r.message.doctype, r.message.name);
		} else {
			frappe.show_alert(__("Unable to create Sales Invoice. <br>") + r.exc);
		}
	}).fail((f) => {
		frappe.show_alert(__("A problem occurred while creating a Sales Invoice. <br>") + f);
	})
}