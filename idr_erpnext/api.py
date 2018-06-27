import frappe
from frappe import _
import json
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

@frappe.whitelist()
def generate_codice_fiscale(first_name, last_name, date_of_birth, gender, place_of_birth):
	from codicefiscale import build

	gender = 'M' if gender == 'Male' else 'F'
	municipality = frappe.db.get_value("Town", place_of_birth, "town_code")

	return build(last_name, first_name, frappe.utils.getdate(date_of_birth), "M" if gender == "Male" else "F", municipality)

@frappe.whitelist()
def validate_codice_fiscale(codice_fiscale):
	from codicefiscale import isvalid

	valid = isvalid(codice_fiscale)
	
	return _("Codice Fiscale is valid") if valid else _("Codice Fiscale is invalid")

@frappe.whitelist()
def get_procedure_data_from_appointment(patient_appointment):
	idr_appointment_type = frappe.db.get_value("Patient Appointment", patient_appointment, "idr_appointment_type")
	rate = frappe.db.get_value("Item Price", {"item_code":idr_appointment_type}, "price_list_rate")

	out = {
		"idr_appointment_type": idr_appointment_type,
		"rate": rate or 0
	}
	
	return out


def idr_physician_after_insert(doc, method):
	#Create Supplier for invoicing
	supplier = frappe.new_doc("Supplier")
	supplier.supplier_name = " ".join(filter(None, [doc.first_name, doc.middle_name, doc.last_name]))
	supplier.supplier_type = "NON SOCI"
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
def idr_get_availability_data1(date, physician):
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
	physician_schedule_name = frappe.db.get_value("Physician", physician, "idr_physician_schedule")
	if physician_schedule_name:
		physician_schedule = frappe.get_doc("IDR Physician Schedule", physician_schedule_name)
		time_per_appointment = frappe.db.get_value("Physician", physician, "time_per_appointment")
	else:
		frappe.throw(_("Dr {0} does not have a Physician Schedule. Add it in Physician master".format(physician)))

	if physician_schedule:
		for t in physician_schedule.time_slots:
			if date == t.slot_date:
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
		fields=["name", "appointment_time", "duration", "status", "idr_procedure_room"])

	#get appointments for other physicians on that day which use a room.
	appointments_requiring_rooms = frappe.get_all(
		"Patient Appointment",
		filters={"physician": ("!=", physician), "appointment_date":date, "idr_procedure_room":("!=","")},
		fields=["name", "appointment_time", "duration", "status", "idr_procedure_room"])

	return {
		"available_slots": available_slots,
		"appointments": appointments,
		"appointments_requiring_rooms": appointments_requiring_rooms,
		"time_per_appointment": time_per_appointment
	}

@frappe.whitelist()
def idr_create_invoice(company, physician, patient, appointment_id, appointment_date):
	if not appointment_id:
		return False
	sales_invoice = frappe.new_doc("Sales Invoice")
	sales_invoice.customer = frappe.get_value("Patient", patient, "customer")
	sales_invoice.appointment = appointment_id
	sales_invoice.idr_physician = frappe.db.get_value("Patient Appointment", appointment_id, "physician")
	sales_invoice.due_date = getdate()
	sales_invoice.is_pos = '0'
	sales_invoice.debit_to = get_receivable_account(company)

	appointment = frappe.get_doc("Patient Appointment", appointment_id)

	default_selling_price_list = frappe.db.get_value("IDR Settings", "IDR Settings", "default_selling_price_list")

	rate = frappe.db.get_value("Item Price", {"item_code":appointment.idr_appointment_type, "price_list":default_selling_price_list}, "price_list_rate")

	sales_invoice.append("items", {
		"item_code": appointment.idr_appointment_type,
		"description":  frappe.db.get_value("Item", appointment.idr_appointment_type, "description"),
		"qty": 1,
		"uom": "Nos",
		"conversion_factor": 1,
		"income_account": get_income_account(physician, company),
		"rate": rate, 
		"amount": rate,
		"item_group": frappe.db.get_value("Item", {"item_code":appointment.idr_appointment_type}, "item_group")
	})
	
	taxes = get_default_taxes_and_charges("Sales Taxes and Charges Template", company=company)

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

def idr_patient_appointment_before_insert(doc, method):
	generate_appointment_description(doc, method) #For displaying in Calendar View (Gorlomi E- BR) when doc is Riccardo Bono, patient Enzo Gorlomi

def generate_appointment_description(doc, method):	
	doc.idr_appointment_description = "{0} {1}. {2}{3}".format(frappe.db.get_value("Patient", doc.patient, "idr_patient_last_name"), 
		frappe.db.get_value("Patient", doc.patient, "idr_patient_first_name")[0].upper(), 
		frappe.db.get_value("Physician", doc.physician, "last_name")[0].upper(), 
		frappe.db.get_value("Physician", doc.physician, "first_name")[0].upper())

@frappe.whitelist()
def get_next_available_slot_and_physician():
	'''
		for each date between the first and last dates of all schedules today onwards including today:
			available_docs = []
			for each soci physician:
				get_slot_count
				get_appointment_count
				if slot_count on date != appointment_count on date:
					add physician and date to available docs
		
	'''
	soci_department = frappe.db.get_value("IDR Settings", "IDR Settings", "member_department")
	soci_physicians_and_schedules = frappe.get_all("Physician", filters={"department":soci_department}, fields=["name", "idr_physician_schedule"])

	soci_physicians = [row.name for row in soci_physicians_and_schedules]
	soci_schedules = [row.idr_physician_schedule for row in soci_physicians_and_schedules]

	all_slot_dates = frappe.get_all("IDR Physician Schedule Time Slot", fields=["slot_date"], \
		distinct=True, order_by="slot_date", filters={"parent": ("in", soci_schedules), "slot_date": (">=", frappe.utils.getdate())})

	all_slot_dates = [slot.slot_date for slot in all_slot_dates]

	available_physicians = []
	for date in all_slot_dates:
		for physician in soci_physicians:
			timeslot_count = frappe.db.count("IDR Physician Schedule Time Slot", 
				filters={
					"slot_date":date,
					"parent":physician
				}
			)
			appointment_count = frappe.db.count("Patient Appointment",
				filters={
					"appointment_date": date,
					"physician":physician
				}
			)
			if timeslot_count > appointment_count:
				available_physicians.append(
					{
					"physician": physician, 
					"date": date, 
					"slot_count":timeslot_count, 
					"appointment_count": appointment_count
				})

	if len(available_physicians) > 0:
		return available_physicians[0]


@frappe.whitelist()
def get_earliest_available_date2(physician, procedure_room=None):
	all_slot_dates = frappe.get_all("IDR Physician Schedule Time Slot", fields=["slot_date"], \
		distinct=True, order_by="slot_date", filters={"parent": physician, "slot_date": (">=", frappe.utils.getdate())})

	all_slot_dates = [slot.slot_date for slot in all_slot_dates]

	for date in all_slot_dates:
		timeslots = frappe.get_all("IDR Physician Schedule Time Slot", 
			filters={
				"slot_date":date,
				"parent":physician
			},
			fields=["slot_date AS date", "from_time AS time"]
		)

		print("Timeslots", len(timeslots))
		appointments = frappe.get_all("Patient Appointment",
			filters={
				"appointment_date": date,
				"physician":physician
			},
			fields=["appointment_date AS date", "appointment_time as time"]
		)
		print("appointments", len(appointments))

		#If there are available slots, check whether rooms are available.
		if len(timeslots) > len(appointments):
			print("Procedure room", procedure_room)
			if not procedure_room:	
				return date
			else:
				#Get all available slots
				#Get confirmed appointments for other doctors during these slots with the same procedure 
				#If length is 0, it is implied that both doctor and room are available on this slot. Return the date.
				available_slots = [timeslot for timeslot in timeslots if timeslot not in appointments]
				available_slot_from_times = ",".join(["'{0}'".format(slot.time) for slot in available_slots])

				print("available_slot_from_times on ", date, available_slot_from_times)

				query = """
					SELECT `tabPatient Appointment`.`name` 
					FROM `tabPatient Appointment` 
					WHERE `tabPatient Appointment`.appointment_date = '{appointment_date}'
					AND `tabPatient Appointment`.physician != '{physician}'
					AND `tabPatient Appointment`.idr_procedure_room = '{procedure_room}' 
					AND `tabPatient Appointment`.appointment_time IN ({appointment_times}) 
					ORDER BY `tabPatient Appointment`.`modified` DESC;
				""".format(appointment_date=date, 
					physician=physician, 
					procedure_room=procedure_room, 
					appointment_times=available_slot_from_times)

				appointments_for_room = frappe.db.sql(query, as_dict=1)

				print ("appointments_for_room", appointments_for_room)

				#If the number of appointments needing a room is less than available slots, return date.
				if len(available_slot_from_times) > len(appointments_for_room):
					return date


@frappe.whitelist()
def get_earliest_available_physician_and_date2(procedure_room=None):
	soci_department = frappe.db.get_value("IDR Settings", "IDR Settings", "member_department")
	soci_physicians = frappe.get_all("Physician", filters={"department":soci_department}, fields=["name"])

	earliest_physician_availability_list = [
		frappe._dict(
			physician=physician.name, 
			earliest_available_date=get_earliest_available_date2(physician.name, procedure_room)
		) for physician in soci_physicians
	]

	print(earliest_physician_availability_list)
	
	#Remove doctors who have no availability date
	earliest_physician_availability_list = filter(lambda x: x.get("earliest_available_date") is not None, earliest_physician_availability_list)

	earliest_available_physician_and_date = min(earliest_physician_availability_list, key=lambda x:x.earliest_available_date)

	return earliest_available_physician_and_date

def idr_physician_on_update(doc, method):
	if doc.idr_physician_schedule and not doc.physician_schedule:
		dummy_schedule = frappe.new_doc("Physician Schedule")
		dummy_schedule.schedule_name = doc.idr_physician_schedule
		dummy_schedule.save()

		doc.db_set("physician_schedule", dummy_schedule.name)
		doc.db_set("time_per_appointment", 20)
		frappe.db.commit()


@frappe.whitelist()
def create_doctor_invoices(filters):
	filters = json.loads(filters)

	for x in xrange(1,10):
		print("FILTERS", filters)

	if len(filters) == 0:
		frappe.throw(_("Please select a doctor and date"))

	filter_dict = frappe._dict(filters)
	
	appointments = frappe.get_all("Patient Appointment", 
		filters={"appointment_date": filter_dict.date, "physician": filter_dict.physician, "sales_invoice":("!=", "")}, 
		fields=["name", "idr_appointment_type", "sales_invoice"]
	);

	if len(appointments) == 0:
		frappe.throw(_("There are appointments without linked invoices for this date and doctor."))

	physician_supplier = frappe.db.get_value("Physician", filter_dict.physician, "idr_supplier")
	physician_supplier_type = frappe.db.get_value("Supplier", physician_supplier, "supplier_type")

	#If appointments already exist in other invoice, throw an error
	appointment_names = [appointment.name for appointment in appointments]
	appointments_in_other_invoices = frappe.get_all("Purchase Invoice Item", 
		filters={"idr_patient_appointment": ('in', appointment_names)}, 
		fields=["parent", "idr_patient_appointment"])

	if len(appointments_in_other_invoices) > 0:
		appointments_in_other_invoices_list = [a.idr_patient_appointment for a in appointments_in_other_invoices]
		other_invoices = [a.parent for a in appointments_in_other_invoices]
		frappe.throw(_("Appointment(s) {0} already added to invoice(s) {1}.").format(", ".join(appointments_in_other_invoices_list), ", ".join(other_invoices)))

	#Make Purchase Invoice for doctor and date.
	purchase_invoice = frappe.new_doc("Purchase Invoice")
	purchase_invoice.supplier = physician_supplier
	purchase_invoice.buying_price_list = "SOCI" if physician_supplier_type == "SOCI" else "NON SOCI"
	purchase_invoice.set_posting_time = 1
	purchase_invoice.posting_date = filter_dict.date

	for appointment in appointments:
		#appointment = frappe.get_doc("Patient Appointment", appointment.name)
		invoice_items = frappe.get_all("Sales Invoice Item", filters={"parent":appointment.sales_invoice}, fields=["*"])

		for invoice_item in invoice_items:
			rate = frappe.db.get_value("Item Price", 
				filters={"price_list": purchase_invoice.buying_price_list, "item_code": invoice_item.item_code}, 
				fieldname="price_list_rate")
			
			#If rate not in soci or non soci.
			if not rate:
				rate = frappe.db.get_value("Item Price", 
				filters={"price_list": "CLIENTI", "item_code": invoice_item.item_code}, 
				fieldname="price_list_rate")

			purchase_invoice.append("items", {
				"item_code": invoice_item.item_code,
				"qty": 1,
				"rate": rate,
				"amount": rate,
				"conversion_factor":1,
				"idr_patient_appointment": appointment.name,
				"idr_patient_appointment_invoice": appointment.sales_invoice
			})

	taxes = get_default_taxes_and_charges("Purchase Taxes and Charges Template", company=frappe.defaults.get_defaults().get("company"))
	
	if taxes.get('taxes'):
		purchase_invoice.update(taxes)

	purchase_invoice.save()
	purchase_invoice.db_set("set_posting_time", 0)

	frappe.msgprint(
		_("Doctor Invoice <a href='desk#Form/Purchase%20Invoice/{0}'>{0}</a> created.".format(purchase_invoice.name))
	)

@frappe.whitelist()
def idr_update_appointment_expenses(appointment, expenses):
	frappe.db.set_value("Patient Appointment", appointment, "idr_extra_expenses", expenses)

def idr_customer_on_update(doc, method):
	#Checks
	if not doc.idr_customer_address_line1 or not doc.idr_customer_address_town or not doc.idr_customer_address_pincode:
		return

	existing_address_name = get_default_address("Customer", doc.name)

	if existing_address_name:
		address = frappe.get_doc("Address", existing_address_name)
	else:
		address = frappe.new_doc("Address")
		address.append('links', {
			"link_doctype": "Customer",
			"link_name": doc.name
		})

	address.address_line1 = doc.idr_customer_address_line1
	address.address_line2 = doc.idr_customer_address_line2
	address.city = doc.idr_customer_address_town
	address.pincode = doc.idr_customer_address_pincode
	address.save()
