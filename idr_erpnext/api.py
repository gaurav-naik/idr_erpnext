import frappe
from frappe.contacts.doctype.address.address import get_address_display, get_default_address
from frappe.contacts.doctype.contact.contact import get_default_contact
from frappe import _

@frappe.whitelist()
def get_patient_address_display(address_name):
	return get_address_display(frappe.get_doc("Address", address_name).as_dict())

@frappe.whitelist()
def create_invoice_for_patient(patient_name):
	si = frappe.new_doc("Sales Invoice")
	si.company = frappe.defaults.get_defaults()["company"]
	si.customer = patient_name
	si.customer_address = get_default_address("Customer", patient_name)
	si.contact_person = get_default_contact("Customer", patient_name)

	return si