import frappe
from frappe.contacts.doctype.address.address import get_address_display, get_default_address
from frappe.contacts.doctype.contact.contact import get_default_contact
from frappe import _

@frappe.whitelist()
def get_patient_address_display(address_name):
	return get_address_display(frappe.get_doc("Address", address_name).as_dict())

@frappe.whitelist()
def create_invoice_for_patient(patient_customer):
	si = frappe.new_doc("Sales Invoice")
	si.company = frappe.defaults.get_defaults()["company"]
	si.customer = patient_customer
	si.customer_address = get_default_address("Customer", patient_customer)
	si.contact_person = get_default_contact("Customer", patient_customer)
	si.due_date = frappe.utils.nowdate()

	return si

@frappe.whitelist()
def generate_codice_fiscale(last_name, first_name, date_of_birth, gender, municipality):
	from codicefiscale import build

	return build(last_name, first_name, date_of_birth, gender, municipality)

@frappe.whitelist()
def get_procedure_data_from_appointment(patient_appointment):

	idr_appointment_type = frappe.db.get_value("Patient Appointment", patient_appointment, "idr_appointment_type")
	rate = frappe.db.get_value("Item Price", {"item_code":idr_appointment_type}, "price_list_rate")

	out = {
		"idr_appointment_type": idr_appointment_type,
		"rate": rate or 0
	}
	
	return out
