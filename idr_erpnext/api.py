import frappe
from frappe.contacts.doctype.address.address import get_address_display, get_default_address
from frappe.contacts.doctype.contact.contact import get_default_contact
from frappe import _
from frappe.utils import getdate, cint

#For Create Sales Invoice Override 
from erpnext.controllers.accounts_controller import get_default_taxes_and_charges
from erpnext.healthcare.doctype.patient_appointment.patient_appointment import get_fee_validity
from erpnext.healthcare.doctype.healthcare_settings.healthcare_settings import get_receivable_account,get_income_account

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
	from codicefiscale import build

	gender = 'M' if gender == 'Male' else 'F'
	municipality = frappe.db.get_value("Town", place_of_birth, "")

	return build(last_name, first_name, date_of_birth, "M" if gender == "Male" else "F", municipality)

@frappe.whitelist()
def validate_codice_fiscale(codice_fiscale):
	from codicefiscale import isvalid
	return isvalid(codice_fiscale)

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

	physician_schedule_name = frappe.db.get_value("Physician", physician, "physician_schedule")
	
	if not physician_schedule_name:
		frappe.throw(_("Dr {0} does not have a Physician Schedule. Add it in Physician master".format(physician)))

	physician_schedule = frappe.get_doc("Physician Schedule", physician_schedule_name)

	if physician_schedule.idr_schedule_type == "Date":
		timeslots = frappe.get_all("Physician Schedule Time Slot", filters={"parent": physician, 
			"idr_date": (">=", frappe.utils.getdate())}, 
			fields=["idr_date", "from_time", "to_time"],
			order_by="idr_date")

		if not timeslots:
			frappe.throw("Dr {0} is not avaialble on this date.".format(physician))

		return timeslots[0].idr_date

	else:

		timeslots = frappe.get_all("Physician Schedule Time Slot", filters={"parent": physician}, fields=["day", "from_time", "to_time"])

		if not timeslots:
			frappe.throw("Dr {0} is not avaialble on this date.".format(physician))

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

	out = frappe._dict(patient_customer=None, missing_details=[])

	patient_customer = frappe.db.get_value("Patient", patient, "customer")
	if not patient_customer:
		frappe.throw(_("Patient {0} does not have a linked customer.").format(patient))
		out.missing_details.append(_("Customer"))
		return out

	out.patient_customer = patient_customer

	customer = frappe.get_doc("Customer", patient_customer)

	#Get existing address. Return 0 if not found.
	existing_address_name = get_default_address("Customer", patient_customer)

	if not existing_address_name:
		out.missing_details.append(_("Address"))
		return out

	existing_address = frappe.get_doc("Address",existing_address_name) 

	#Get existing customer
	if not customer.idr_customer_place_of_birth:
		out.missing_details.append(_("Place of Birth"))

	if not customer.idr_customer_date_of_birth:
		out.missing_details.append(_("Date of Birth"))

	if not customer.tax_id:
		out.missing_details.append(_("Tax ID"))

	if not existing_address.address_line1:
		out.missing_details.append(_("Address Line 1"))

	if not existing_address.city:
		out.missing_details.append(_("City"))		

	if not existing_address.pincode:
		out.missing_details.append(_("Pincode"))

	return out

@frappe.whitelist()
def idr_get_availability_data(date, physician):
	"""
	Get availability data of 'physician' on 'date'
	:param date: Date to check in schedule
	:param physician: Name of the physician
	:return: dict containing a list of available slots, list of appointments and time of appointments
	"""
	date = getdate(date)
	weekday = date.strftime("%A")

	available_slots = []
	physician_schedule_name = None
	physician_schedule = None
	time_per_appointment = None

	# get physicians schedule
	physician_schedule_name = frappe.db.get_value("Physician", physician, "physician_schedule")
	if physician_schedule_name:
		physician_schedule = frappe.get_doc("Physician Schedule", physician_schedule_name)
		time_per_appointment = frappe.db.get_value("Physician", physician, "time_per_appointment")
	else:
		frappe.throw(_("Dr {0} does not have a Physician Schedule. Add it in Physician master".format(physician)))

	if physician_schedule:
		if physician_schedule.idr_schedule_type == "Date":
			for t in physician_schedule.time_slots:
				if date == t.idr_date:
					available_slots.append(t)
		else:
			for t in physician_schedule.time_slots:
				if weekday == t.day:
					available_slots.append(t)
			
	
	# `time_per_appointment` should never be None since validation in `Patient` is supposed to prevent
	# that. However, it isn't impossible so we'll prepare for that.
	if not time_per_appointment:
		frappe.throw(_('"Time Per Appointment" hasn"t been set for Dr {0}. Add it in Physician master.').format(physician))

	# if physician not available return
	if not available_slots:
		# TODO: return available slots in nearby dates
		frappe.throw(_("Physician not available on {0}").format(weekday))

	# if physician on leave return

	# if holiday return
	# if is_holiday(weekday):

	# get appointments on that day for physician
	appointments = frappe.get_all(
		"Patient Appointment",
		filters={"physician": physician, "appointment_date": date},
		fields=["name", "appointment_time", "duration", "status"])

	return {
		"available_slots": available_slots,
		"appointments": appointments,
		"time_per_appointment": time_per_appointment
	}

@frappe.whitelist()
def idr_create_invoice(company, physician, patient, appointment_id, appointment_date):
	if not appointment_id:
		return False
	sales_invoice = frappe.new_doc("Sales Invoice")
	sales_invoice.customer = frappe.get_value("Patient", patient, "customer")
	sales_invoice.appointment = appointment_id
	sales_invoice.due_date = getdate()
	sales_invoice.is_pos = '0'
	sales_invoice.debit_to = get_receivable_account(company)

	appointment = frappe.get_doc("Patient Appointment", appointment_id)

	rate = frappe.db.get_value("Item Price", {"item_code":appointment.idr_appointment_type}, "price_list_rate")

	sales_invoice.append("items", {
		"item_code": appointment.idr_appointment_type,
		"description":  frappe.db.get_value("Item", appointment.idr_appointment_type, "description"),
		"qty": 1,
		"uom": "Nos",
		"conversion_factor": 1,
		"income_account": get_income_account(physician, company),
		"rate": rate, 
		"amount": rate
	})
	
	taxes = get_default_taxes_and_charges("Sales Taxes and Charges Template", company=company)

	print("Taxes", taxes)

	if taxes.get('taxes'):
		sales_invoice.update(taxes)
	
	sales_invoice.save(ignore_permissions=True)
	
	fee_validity = get_fee_validity(physician, patient, appointment_date)

	frappe.db.sql("""update `tabPatient Appointment` set sales_invoice=%s where name=%s""", (sales_invoice.name, appointment_id))
	frappe.db.set_value("Fee Validity", fee_validity.name, "ref_invoice", sales_invoice.name)
	consultation = frappe.db.exists({
			"doctype": "Consultation",
			"appointment": appointment_id})
	if consultation:
		frappe.db.set_value("Consultation", consultation[0][0], "invoice", sales_invoice.name)

	return sales_invoice.name
