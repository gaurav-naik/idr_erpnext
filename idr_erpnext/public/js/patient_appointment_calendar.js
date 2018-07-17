frappe.views.calendar["Patient Appointment"] = {       
	field_map: {
		"allDay": "idr_allday",
		"title": "idr_appointment_description",
		"start": "appointment_date",
		"end": "idr_appointment_endtime",
		"id": "name",
		"doctype": "Patient Appointment",
		"color": "color"
	},
	get_calendar_options: function() {
		console.log("CALHACK");
	},
	gantt: false,
	get_events_method: "erpnext.healthcare.doctype.patient_appointment.patient_appointment.get_events"
}