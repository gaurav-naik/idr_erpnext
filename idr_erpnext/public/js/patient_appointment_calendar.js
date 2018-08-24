frappe.views.calendar["Patient Appointment"] = {
	field_map: {
		"title": "idr_appointment_description"
	},
	gantt: false,
	get_events_method: "idr_erpnext.api.idr_appointment_get_events"
}