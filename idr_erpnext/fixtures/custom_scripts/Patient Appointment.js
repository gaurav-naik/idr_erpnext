frappe.ui.form.on("Patient Appointment", {
	onload: function(frm) {
		//Check if patient info is filled
		check_patient_details(frm);
	},
	refresh: function(frm) {
		if (frm.doc.__islocal) {
			frm.add_custom_button(__("Check Availability"), function() {
				check_patient_availability(frm);
			});
		}

		if (frm.doc.sales_invoice) {
			frm.add_custom_button(__("Delete Linked Invoice"), function() {
				frappe.call({
					method:"idr_erpnext.api.unlink_and_delete_sales_invoice",
					args: {
						patient_appointment: frm.doc.name
					},
					freeze: true,
					freeze_message: __("Deleting linked invoice...")
				}).done(function(r) {
					frm.reload_doc();
				}).error(function(r) {
					frappe.show_alert(__("Cannot unlink sales invoice"));
				});
			});
		}

		frm.add_custom_button(__("Update Expenses"), function() {
			let dialog = new frappe.ui.Dialog({
				title: __('Update Expenses'),
				fields: [
					{
						reqd: 1,
						label: 'Expenses',
						fieldtype: 'Currency',
						fieldname: 'expenses',
					}
				]
			});
			dialog.set_value('expenses', frm.doc.idr_extra_expenses);
			dialog.set_primary_action(__("Update"), () => {
				let values = dialog.get_values();
				if(values) {
					// Set the default_supplier field of the appropriate Item to the selected supplier
					frappe.call({
						method: "idr_erpnext.api.idr_update_appointment_expenses",
						args: {
							appointment: frm.doc.name,
							expenses: values.expenses
						},
						freeze: true,
						callback: (r) => {
							refresh_field('idr_extra_expenses');
							frappe.show_alert(__("Successfully updated expenses"));
							dialog.hide();
						}
					});
				}
			});
			dialog.show();
		});

		//Check if patient info is filled
		check_patient_details(frm);
	},
	idr_appointment_type: function(frm) {
		if (!frm.doc.patient) { return 0; }
		frappe.call({
			method: "idr_erpnext.api.get_earliest_available_physician_and_date2", //get_earliest_available_physician_and_date"// get_physician_with_earliest_timeslot"
			args: {
				"procedure_room": frm.doc.idr_procedure_room
			}
		}).done(function(r) {
			console.log("Physician", r);
			if (!r.exc) {
				frm.set_value("physician", r.message.physician);
			}
		}).error(function(err) {
			frappe.show_alert(__("Could not fetch earliest available doctor."));
		});
		check_patient_details(frm);
	},
	physician: function(frm) {
		if (!frm.doc.physician) { return 0; }
		frappe.call({
			method: "idr_erpnext.api.get_earliest_available_date2",
			args: {
				"physician": frm.doc.physician,
				"procedure_room": frm.doc.idr_procedure_room
			}
		}).done(function(r) {
			if (!r.exc) {
				frm.set_value("appointment_date", r.message);
			}
		}).error(function(err) {
			frappe.show_alert(__("Could not fetch earliest available date."));
		});
	},
	appointment_date: function(frm) {
		if (frm.doc.appointment_date) {
			check_patient_details(frm);
		}
	}
});

frappe.ui.keys.on("alt+c", function(e) {
	frappe.click_button("Check Availability");
});

function check_patient_details(frm) {
	if (frm.doc.patient) {
		frappe.call({
			method: "idr_erpnext.api.check_patient_details",
			args: {
				patient: frm.doc.patient,
			}
		}).done(function(r) {
			console.log(r);
			if (r && r.message && r.message.missing_details && r.message.missing_details.length > 0) {
				frm.set_df_property("patient", "label", 
					__("Patient") + '<a class="badge" style="color:white;background-color:red" href="/desk#Form/Customer/' + r.message.patient_customer + '">' 
					+ __("Customer information missing!") + '</a>'
				);
				$("button[data-doctype='Sales Invoice'].btn-new").attr('disabled', 'disabled');

				if (cur_frm.custom_buttons["Invoice"]) {
					cur_frm.custom_buttons["Invoice"].hide();
				}
			} else {
				frm.set_df_property("patient", "label", __("Patient"));
				$("button[data-doctype='Sales Invoice'].btn-new").removeAttr('disabled');

				if (cur_frm.custom_buttons["Invoice"]) {
					cur_frm.custom_buttons["Invoice"].show();
				}
			}
		}).error(function(err) {
			frappe.show_alert(__("Could not check patient details"));
		});
	}
}

//CLONE Check patient availability
function check_patient_availability(frm) {
	var { physician, appointment_date } = frm.doc;
	if(!(physician && appointment_date)) {
		frappe.throw(__("Please select Physician and Date"));
	}

	// show booking modal
	frm.call({
		method: 'idr_erpnext.api.idr_get_availability_data1',
		args: {
			physician: physician,
			date: appointment_date
		},
		callback: (r) => {
			// console.log(r);
			var data = r.message;
			if(data.available_slots.length > 0) {
				show_availability(data);
			} else {
				show_empty_state();
			}
		}
	});

	function show_empty_state() {
		frappe.msgprint({
			title: __('Not Available'),
			message: __("Physician {0} not available on {1}", [physician.bold(), appointment_date.bold()]),
			indicator: 'red'
		});
	}

	function show_availability(data) {
		console.log("slots", data.available_slots);
		console.log("appointments", data.appointments);
		console.log("room_appointments", data.appointments_requiring_rooms);

		var d = new frappe.ui.Dialog({
			title: __("Available slots"),
			fields: [{ fieldtype: 'HTML', fieldname: 'available_slots'}],
			primary_action_label: __("Book"),
			primary_action: function() {
				// book slot
				frm.set_value('appointment_time', selected_slot);
				frm.set_value('duration', data.time_per_appointment);
				d.hide();
				frm.save();
			}
		});
		var $wrapper = d.fields_dict.available_slots.$wrapper;
		var selected_slot = null;

		// disable dialog action initially
		d.get_primary_btn().attr('disabled', true);

		// make buttons for each slot
		var slot_html = data.available_slots.map(slot => {
			return `<button class="btn btn-default"
				data-name=${slot.from_time} data-room=${slot.idr_procedure_room}
				style="margin: 0 10px 10px 0; width: 72px">
				${slot.from_time.substring(0, slot.from_time.length - 3)}
			</button>`;
		}).join("");

		$wrapper
			.css('margin-bottom', 0)
			.addClass('text-center')
			.html(slot_html);

		// disable buttons for which appointments are booked
		data.appointments.map(slot => {
			console.log(slot)
			if(slot.status == "Scheduled" || slot.status == "Open" || slot.status == "Closed"){
				$wrapper
					.find(`button[data-name="${slot.appointment_time}"]`)
					.attr('disabled', true)
					.addClass('btn-danger');
			}
		});

		data.appointments_requiring_rooms.map(slot => {
			if(slot.idr_procedure_room == frm.doc.idr_procedure_room){
				$wrapper
					.find(`button[data-name="${slot.appointment_time}"]`)
					.attr('disabled', true)
					.addClass('btn-danger');
			}
		});

		// blue button when clicked
		$wrapper.on('click', 'button', function() {
			var $btn = $(this);
			$wrapper.find('button').removeClass('btn-primary');
			$btn.addClass('btn-primary');
			selected_slot = $btn.attr('data-name');

			// enable dialog action
			d.get_primary_btn().attr('disabled', null);
		});

		d.show();
	}
}