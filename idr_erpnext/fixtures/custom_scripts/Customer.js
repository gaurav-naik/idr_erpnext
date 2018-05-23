frappe.ui.form.on("Customer", {
	onload: function(frm) {
		frm.fields_dict.idr_codice_fiscale_buttons.html(
			'<button class="btn btn-xs btn-default generate-cf">' + __("Generate") + '</button>' +
			'<button class="btn btn-xs btn-default validate-cf">' + __("Validate") + '</button>'
		);

		$(".generate-cf").on("click", function() {
			frappe.call({
				method: "idr_erpnext.api.generate_codice_fiscale",
				args: {
					first_name: frm.doc.idr_customer_first_name, 
					last_name: frm.doc.idr_customer_last_name, 
					date_of_birth: frm.doc.idr_customer_date_of_birth, 
					gender: frm.doc.idr_customer_gender, 
					place_of_birth: frm.doc.idr_customer_place_of_birth
				}
			}).done(function(r) {
				frm.set_value("idr_customer_tax_id", r.message);
				frm.refresh();
			}).error(function(err) {
				frappe.show_alert(__("Unable to set codice fiscale"));
			});
		});
		$(".validate-cf").on("click", function() {
			frappe.call({
				method: "idr_erpnext.api.validate_codice_fiscale",
				args: {
					codice_fiscale: frm.doc.idr_customer_tax_id, 
				}
			}).done(function(r) {
				frm.refresh();
				frappe.msgprint(r.message);
			}).error(function(err) {
				frm.show_alert(__("Unable to set codice fiscale"));
			});
		});
	},
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