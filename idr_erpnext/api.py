import frappe
from frappe.contacts.doctype.address.address import get_address_display, get_default_address

@frappe.whitelist()
def get_patient_address_display(address_name):
	return get_address_display(frappe.get_doc("Address", address_name).as_dict())
	