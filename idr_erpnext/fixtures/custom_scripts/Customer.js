frappe.ui.form.on("Customer", {
	idr_customer_gender: function(frm) {
		frm.set_value("gender", frm.doc.idr_customer_gender);
	},
	idr_customer_tax_id:function(frm) {
		frm.set_value("tax_id", frm);
	}
});