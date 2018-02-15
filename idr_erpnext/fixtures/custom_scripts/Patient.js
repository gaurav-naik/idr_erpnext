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
		add_make_sales_invoice_button(frm);
	}
})

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

function add_make_sales_invoice_button(frm) {
	if (!frm.doc.__islocal) {
		frm.add_custom_button(__('Sales Invoice'), function() {
			frappe.call({
				method: "idr_erpnext.api.create_invoice_for_patient",
				args: {
					patient_name: frm.doc.patient_name
				}
			}).done((r) => {
				if (!r.exc) {
					frappe.model.sync(r.message);
					frappe.set_route("Form", r.message.doctype, r.message.name);
				} else {
					frappe.show_alert(_("Unable to create Sales Invoice. <br>") + r.exc);
				}
			}).fail((f) => {
				frappe.show_alert(_("A problem occurred while creating a Sales Invoice. <br>") + f);
			})
		},__("Create"));
	}
}