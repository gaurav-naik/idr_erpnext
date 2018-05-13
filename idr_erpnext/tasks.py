import frappe


def daily():
	execute_appointment_housekeeping()

def execute_appointment_housekeeping():
	appointments = frappe.get_all("Patient Appointment", 
		filters={"appointment_date": ("<", frappe.utils.getdate()), "sales_invoice":""})

	for appointment in appointments:
		frappe.delete_doc("Patient Appointment", appointment.name)

	frappe.db.commit()
