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
def generate_codice_fiscale(first_name, last_name, date_of_birth, gender, place_of_birth):
	for x in xrange(1,10):
		print (first_name, last_name, date_of_birth, gender, place_of_birth)

	# from codicefiscale import build

	# return build(last_name, first_name, date_of_birth, "M" if gender == "Male" else "F", municipality)

@frappe.whitelist()
def get_procedure_data_from_appointment(patient_appointment):
	idr_appointment_type = frappe.db.get_value("Patient Appointment", patient_appointment, "idr_appointment_type")
	rate = frappe.db.get_value("Item Price", {"item_code":idr_appointment_type}, "price_list_rate")

	out = {
		"idr_appointment_type": idr_appointment_type,
		"rate": rate or 0
	}
	
	return out


def physician_after_insert(doc, method):
	#Create Supplier for invoicing
	supplier = frappe.new_doc("Supplier")
	supplier.supplier_name = " ".join(filter(None, [doc.first_name, doc.middle_name, doc.last_name]))
	supplier.supplier_type = "Non Member"
	supplier.save()

	doc.db_set("idr_supplier", supplier.name)
	frappe.db.commit()
	#TODO: create tax rules
	

def patient_on_update(doc, method):
	if not doc.customer:
		return

	existing_address = frappe.get_all("Dynamic Link", 
		filters={"link_doctype":"Customer", "link_name":doc.customer, "parenttype":"Address"}, fields=["parent"])
	existing_contact = frappe.get_all("Dynamic Link", 
		filters={"link_doctype":"Customer", "link_name":doc.customer, "parenttype":"Contact"}, fields=["parent"]) 

	#Create Address and link to customer.
	address = None	
	if len(existing_address) > 0:
		address = frappe.get_doc("Address", existing_address.parent)
	else:
		address = frappe.new_doc("Address")

	address.title = doc.patient_name
	address.type = "Billing"
	address.address_line1 = doc.idr_address_line1
	address.address_line2 = doc.idr_address_line2
	address.city = doc.idr_address_city
	address.pincode = doc.idr_address_pincode
	address.country = frappe.defaults.get_defaults().get("country")
	address.is_primary_address = 1
	address.append('links', {
		"link_doctype": "Customer",
		"link_name": doc.customer
	})
	try:
		address.save()
	except Exception as e:
		raise

	contact = None
	if len(existing_contact) > 0:
		contact = frappe.get_doc("Contact", existing_contact.parent) 
	else:	
		contact = frappe.new_doc("Contact")
		
	contact_name = doc.patient_name.split(" ")
	contact.first_name = contact_name[0]
	if len(contact_name) > 1:
		contact.last_name = contact_name[1]
	contact.mobile_no = doc.mobile
	contact.gender = doc.sex
	contact.phone = doc.phone
	contact.is_primary_contact = 1

	contact.append('links', {
		"link_doctype": "Customer",
		"link_name": doc.customer
	})

	try:
		contact.save()
	except Exception as e:
		raise
	
	frappe.db.set_value("Customer", doc.customer, "customer_name", doc.patient_name)
