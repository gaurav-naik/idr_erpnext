frappe.ui.form.on("Physician Schedule", {
	idr_schedule_type: function(frm) {
		if (frm.doc.idr_schedule_type == "Day of Week") {
			cur_frm.fields_dict.references.grid.set_column_disp("date", false);
			cur_frm.fields_dict.references.grid.set_column_disp("idr_day_of_week", true);
		} else (frm.doc.idr_schedule_type == "Date") {
			cur_frm.fields_dict.references.grid.set_column_disp("date", true);
			cur_frm.fields_dict.references.grid.set_column_disp("idr_day_of_week", false);
		}
	}
});