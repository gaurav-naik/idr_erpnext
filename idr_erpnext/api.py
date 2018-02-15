import frappe
from frappe.contacts.doctype.address.address import get_address_display, get_default_address
from frappe.contacts.doctype.contact.contact import get_default_contact
from frappe import _

@frappe.whitelist()
def get_patient_address_display(address_name):
	return get_address_display(frappe.get_doc("Address", address_name).as_dict())


def create_customer_against_patient(self, method):
	settings = frappe.get_doc("Healthcare Settings")

	if not settings.manage_customer:
		
		customer_group = frappe.get_value("Selling Settings", None, "customer_group")
		territory = frappe.get_value("Selling Settings", None, "territory")
		if not (customer_group and territory):
			customer_group = "Commercial"
			territory = "Rest Of The World"
			frappe.msgprint(_("Please set default customer group and territory in Selling Settings"), alert=True)
		
		customer = frappe.get_doc({"doctype": "Customer",
		"customer_name": self.patient_name,
		"customer_group": customer_group,
		"territory" : territory,
		"customer_type": "Individual"
		}).insert(ignore_permissions=True)

		frappe.db.set_value("Patient", self.name, "customer", customer.name)

		frappe.msgprint(_("Customer {0} created.").format(customer.name), alert=True)

@frappe.whitelist()
def create_invoice_for_patient(patient_name):
	si = frappe.new_doc("Sales Invoice")
	si.company = frappe.defaults.get_defaults()["company"]
	si.customer = patient_name
	si.customer_address = get_default_address("Customer", patient_name)
	si.contact_person = get_default_contact("Customer", patient_name)
	
	return si