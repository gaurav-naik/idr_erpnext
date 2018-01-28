import frappe
from frappe.contacts.doctype.address.address import get_address_display, get_default_address

@frappe.whitelist()
def get_patient_address_display(linked_customer):
	return get_address_display(frappe.get_doc("Address", get_default_address("Customer", linked_customer)).as_dict()) or "-"