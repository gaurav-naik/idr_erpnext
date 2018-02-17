frappe.ui.form.on("Sales Invoice", {
	"onload_post_render": function(frm) {
		//Scroll directly to items if Invoice has been opened from Patient doctype.
		var last_route = frappe.route_history.slice(-2, -1)[0];
		if (last_route && last_route[0] == "Form" && last_route[1] == "Patient") {
			frappe.model.add_child(cur_frm.doc, "Sales Invoice Item", "items", 0);
			refresh_field("items");
 			frappe.ui.scroll("[data-fieldname='currency']", true);
		}
	}
})