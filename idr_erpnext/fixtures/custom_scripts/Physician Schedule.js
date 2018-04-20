frappe.ui.form.on("Physician Schedule", {
	refresh: function(frm) {
		frm.add_custom_button(__('Add Time Slots by Date'), () => {
			var d = new frappe.ui.Dialog({
				fields: [
					{fieldname: 'idr_date', label: __('Date'), fieldtype:'Date'},
					{fieldname: 'from_time', label:__('From'), fieldtype:'Time',
						'default': '09:00:00', reqd: 1},
					{fieldname: 'to_time', label:__('To'), fieldtype:'Time',
						'default': '12:00:00', reqd: 1},
					{fieldname: 'duration', label:__('Appointment Duration (mins)'),
						fieldtype:'Int', 'default': 15, reqd: 1},
				],
				primary_action_label: __('Add Timeslots'),
				primary_action: () => {
					var values = d.get_values();
					if(values) {
						let cur_time = moment(values.from_time, 'HH:mm:ss');
						let end_time = moment(values.to_time, 'HH:mm:ss');

						while(cur_time < end_time) {
							let to_time = cur_time.clone().add(values.duration, 'minutes');
							if(to_time <= end_time) {

								// add a new timeslot
								frm.add_child('time_slots', {
									from_time: cur_time.format('HH:mm:ss'),
									to_time: to_time.format('HH:mm:ss'),
									idr_date: values.idr_date
								});
							}
							cur_time = to_time;
						}

						frm.refresh_field('time_slots');
						frappe.show_alert({
							message:__('Time slots added'),
							indicator:'green'
						});
					}
				},
			});
			d.show();
		});
		frm.trigger("manage_custom_button_visibility");
		frm.trigger("manage_date_day_field_visibility");
	},
	idr_schedule_type: function(frm) {
		frm.trigger("manage_custom_button_visibility");
		frm.trigger("manage_date_day_field_visibility");
		// if (frm.doc.idr_schedule_type == "Day of Week") {
		// 	frm.fields_dict.time_slots.grid.set_column_disp("idr_date", false);
		// 	frm.fields_dict.time_slots.grid.set_column_disp("day", true);
		// 	frm.doc.custom_button["Add Time Slots"].show();
		// 	frm.doc.custom_button["Add Time Slots by Date"].hide();
		// } else if (frm.doc.idr_schedule_type == "Date") {
		// 	frm.fields_dict.time_slots.grid.set_column_disp("idr_date", true);
		// 	frm.fields_dict.time_slots.grid.set_column_disp("day", false);
		// 	frm.doc.custom_button["Add Time Slots"].hide();
		// 	frm.doc.custom_button["Add Time Slots by Date"].show();
		// }
	},
	manage_custom_button_visibility: function(frm) {
		if (frm.doc.idr_schedule_type == "Date") {
			frm.custom_buttons["Add Time Slots"].hide();
			frm.custom_buttons["Add Time Slots by Date"].show();
		} else {
			frm.custom_buttons["Add Time Slots"].show();
			frm.custom_buttons["Add Time Slots by Date"].hide();
		}
	},
	manage_date_day_field_visibility: function(frm) {
		if (frm.doc.idr_schedule_type == "Date") {
			frm.fields_dict.time_slots.grid.set_column_disp("idr_date", true);
			frm.fields_dict.time_slots.grid.set_column_disp("day", false);
		} else {
			frm.fields_dict.time_slots.grid.set_column_disp("idr_date", false);
			frm.fields_dict.time_slots.grid.set_column_disp("day", true);
		}
	}
});
