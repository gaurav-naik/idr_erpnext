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
	# from codicefiscale import build
	# return build(last_name, first_name, date_of_birth, "M" if gender == "Male" else "F", municipality)
	pass

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

	frappe.db.set_value("Customer", doc.customer, "customer_name", doc.patient_name)
	frappe.db.set_value("Customer", doc.customer, "idr_customer_first_name", doc.idr_patient_first_name)
	frappe.db.set_value("Customer", doc.customer, "idr_customer_last_name", doc.idr_patient_last_name)

	existing_contact = frappe.get_all("Dynamic Link", 
		filters={"link_doctype":"Customer", "link_name":doc.customer, "parenttype":"Contact"}, fields=["parent"]) 


	contact = None
	if len(existing_contact) > 0:
		contact = frappe.get_doc("Contact", existing_contact[0].parent) 
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
	
@frappe.whitelist()
def get_earliest_available_date(physician):
	'''
		extract days of week from timeslots for physician
		get earliest next date from today by comparing 'day.weekday' in slot and today's 'day.weekday'
		get minimum of all dates

	'''
	def get_next_weekday(d, weekday):
	    days_ahead = weekday - d.weekday()
	    if days_ahead <= 0: # Target day already happened this week
	        days_ahead += 7
	    return d + frappe.utils.datetime.timedelta(days_ahead)

	def get_weekday_value(weekday):
		return {
			"Monday": 0,
			"Tuesday": 1,
			"Wednesday": 2,
			"Thursday": 3,
			"Friday": 4,
			"Saturday": 5,
			"Sunday": 6
		}[weekday]

	timeslots = frappe.get_all("Physician Schedule Time Slot", filters={"parent": physician}, fields=["day", "from_time", "to_time"])

	weekdays = list(set([timeslot.day for timeslot in timeslots]))
	weekdays_with_dow_values = [{"day": weekday, "value": get_weekday_value(weekday)} for weekday in weekdays]

	next_weekdays = [get_next_weekday(frappe.utils.getdate(), weekday.get("value")) for weekday in weekdays_with_dow_values]
	
	next_earliest_weekday_date = min(next_weekdays)

	return next_earliest_weekday_date 

@frappe.whitelist()
def get_earliest_available_physician_and_date():
	'''
		get SOCI doctors
		get earliest timeslots for each doctor
		return earliest among them.
	''' 
	soci_department = frappe.db.get_value("IDR Settings", "IDR Settings", "member_department")
	soci_physicians = frappe.get_all("Physician", filters={"department":soci_department})

	earliest_physician_availability_list = [
		{
			"physician": physician.name, 
			"earliest_available_date": get_earliest_available_date(physician.name)
		} for physician in soci_physicians
	]

	print (earliest_physician_availability_list)

	earliest_physician_availability = min(earliest_physician_availability_list, key=lambda x:x.get("earliest_available_date"))

	return earliest_physician_availability

@frappe.whitelist()
def unlink_and_delete_sales_invoice(patient_appointment):
	sales_invoice = frappe.get_doc("Sales Invoice", {"appointment": patient_appointment})


	if sales_invoice.docstatus == 1:
		frappe.throw(_("Cannot delete a submitted Sales Invoice"))

	fee_validity_name = frappe.db.get_value("Fee Validity", {"ref_invoice": sales_invoice.name})

	try:
		frappe.db.set_value("Sales Invoice", sales_invoice.name, "appointment", None)
		frappe.db.set_value("Patient Appointment", patient_appointment, "sales_invoice", None)
		frappe.db.set_value("Fee Validity", fee_validity_name, "ref_invoice", None)
	except Exception as e:
		raise

	#Delete doc
	frappe.delete_doc("Sales Invoice", sales_invoice.name)
	frappe.db.commit()
	
@frappe.whitelist()
def check_patient_details(patient):
	#Check if Customer has First Name, Last Name, Place of Birth, Tax ID, Phone Number (Contact)

	patient_customer = frappe.db.get_value("Patient", patient, "customer")

	if not patient_customer:
		return "0"

	customer_tax_id = frappe.db.get_value("Customer", patient_customer, "tax_id")
	
	#Get existing address. Return 0 if not found.
	existing_address_name = get_default_address("Customer", patient_customer)

	if not existing_address_name:
		return "0"

	existing_address = frappe.get_doc("Address",existing_address_name) 
	
	#Get existing customer
	out = existing_address.address_line1 is not None and \
	existing_address.city is not None and \
	existing_address.pincode is not None and \
	customer_tax_id is not None

	return "1" if out == True else "0"

