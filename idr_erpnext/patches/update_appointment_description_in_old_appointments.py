import frappe

def execute():
	frappe.reload_doc("healthcare", "doctype", "patient_appointment")
	
	appointments = frappe.get_all("Patient Appointment", fields=["name", "patient_name", "physician"])
	for appointment in appointments:
		description = appointment.patient_name + "-" + ".".join([physician[0] for physician in appointment.physician.split(" ")]) + "."
		frappe.db.set_value("Patient Appointment", appointment.name, "idr_appointment_description", description)
