import frappe
from frappe.contacts.doctype.address.address import get_address_display, get_default_address
from frappe.contacts.doctype.contact.contact import get_default_contact
from frappe import _

@frappe.whitelist()
def get_patient_address_display(address_name):
	return get_address_display(frappe.get_doc("Address", address_name).as_dict())

# Discontinued after using Patient Appointment flow
# @frappe.whitelist()
# def create_invoice_for_patient(patient_customer):
# 	si = frappe.new_doc("Sales Invoice")
# 	si.company = frappe.defaults.get_defaults()["company"]
# 	si.customer = patient_customer
# 	si.customer_address = get_default_address("Customer", patient_customer)
# 	si.contact_person = get_default_contact("Customer", patient_customer)
# 	si.due_date = frappe.utils.nowdate()

# 	return si

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

@frappe.whitelist()
def physician_after_insert(self, method):
	#Create Supplier for invoicing
	supplier = frappe.new_doc("Supplier")
	supplier.supplier_name = " ".join([self.first_name, self.middle_name, self.last_name])
	supplier.supplier_type = "Member" if self.is_member else "Non Member"
	supplier.save()

	self.db_set("idr_supplier", supplier.name)

	#TODO: create tax rules
	
@frappe.whitelist()
def patient_after_insert(self, method):
	#Create contact and address and link to customer
	address = frappe.new_doc("Address")
	address.title = self.patient_name
	address.address_line1 = self.idr_address_line1
	address.address_line2 = self.idr_address_line2
	address.city = self.idr_city
	addres.pincode = self.idr_pincode
	address.country = frappe.defaults.get_defaults().get("country")
	address.append('links', {
		"link_doctype": "Customer",
		"link_name": self.customer
	})
	address.save()

	contact = frappe.new_doc("Contact")
	contact.first_name = self.patient_name.split(" ")[0]
	contact.last_name = self.patient_name.split(" ")[0] or ""
	address.append('links', {
		"link_doctype": "Customer",
		"link_name": self.customer
	})
	contact.save()

	frappe.db.commit()

	#Rename Customer
	frappe.rename_doc("Customer", self.customer, self.patient_name)