frappe.ui.form.on("Customer", {
	idr_customer_gender: function(frm) {
		frm.set_value("gender", frm.doc.idr_customer_gender);
	},
	idr_customer_tax_id:function(frm) {
		frm.set_value("tax_id", frm.doc.idr_customer_tax_id);
	},
	idr_customer_first_name: function(frm) {
		make_customer_name(frm.doc.idr_customer_first_name, frm.doc.idr_customer_last_name);
	},
	idr_customer_last_name: function(frm) {
		make_customer_name(frm.doc.idr_customer_first_name, frm.doc.idr_customer_last_name);
	}
});

function make_customer_name(first_name, last_name) {
	var full_name = first_name + " " + last_name;
	frm.set_value("customer_name", full_name);
}