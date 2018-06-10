# Copyright (c) 2013, Massimiliano Corvino and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from idr_erpnext.idr_erpnext.doctype.idr_settings.idr_settings import get_idr_fee_rate

def execute(filters=None):
	columns, data = get_columns(), get_data(filters)
	return columns, data

def get_columns():
	return [
		{
			"fieldname": "date",
			"label": _("Date"),
			"fieldtype": "Date",
			"width": 90
		},
		{
			"fieldname": "patient_name",
			"label": _("Patient Name"),
			"fieldtype": "Data",
			"width": 220
		},
		{
			"fieldname": "payment_amount",
			"label": _("Payment Amount"),
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"fieldname": "room_charge_percentage",
			"label": _("% Room"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "room_charge_amount",
			"label": _("Room Amount"),
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"fieldname": "doctor_amount",
			"label": _("Doctor Amount + Expenses"),
			"fieldtype": "Currency",
			"width": 200
		},
	]

def get_data(filters):
	'''
		get appointments
		get invoices for all appointments
		get dict where {"item":"item", "item_amount": item_amount, }

		date, patient, sum of invoice rates by CLIENTI, sum of invoice rates by SOCI
	'''
	data = []

	appointments = frappe.get_all("Patient Appointment", 
		filters={"appointment_date": ("between", [filters.get("from_date"), filters.get("to_date")]), 
			"physician":filters.get("physician"), "sales_invoice":("!=", "")},
		fields=["*"],
		order_by="appointment_date")

	for appointment in appointments:
		row = {"date": appointment.appointment_date, "patient_name": appointment.patient_name}

		invoices = frappe.get_all("Sales Invoice", {"appointment":appointment.name})
		invoice_names = [invoice.name for invoice in invoices]

		invoice_items = frappe.get_all("Sales Invoice Item", filters={"parent": ("in", invoice_names)}, fields=["*"])
		
		#Invoice item totals.
		physician_dept = frappe.db.get_value("Physician", appointment.physician, "department")
		physician_price_list = physician_dept or "CLIENTI"

		total_selling_rate, total_physician_rate = 0, 0
		procedure_type_fee_rates = []
		for invoice_item in invoice_items:
			total_selling_rate += invoice_item.rate or 0
			total_physician_rate += frappe.db.get_value("Item Price", 
				filters={"price_list": physician_price_list, "item_code":invoice_item.item_code}, fieldname="price_list_rate") or 0
			
			item_group = invoice_item.item_group or frappe.db.get_value("Item", invoice_item.item_code, "item_group")

			procedure_type_fee_rates.append(str(get_idr_fee_rate(procedure_type=item_group, physician_category=physician_price_list)))

		row["payment_amount"] = total_selling_rate
		row["room_charge_percentage"] = " + ".join(procedure_type_fee_rates)
		row["room_charge_amount"] = total_selling_rate - total_physician_rate
		row["doctor_amount"] = total_physician_rate

		data.append(row)

	#grand totals

	grand_total_doctor_amount = sum([data_row.get("doctor_amount") for data_row in data])
	ritenuta_amount = grand_total_doctor_amount * 0.2 #@20%

	data.append({
		"payment_amount": sum([data_row.get("payment_amount") for data_row in data]),
		"room_charge_amount": sum([data_row.get("room_charge_amount") for data_row in data]),
		"doctor_amount": grand_total_doctor_amount
	})

	#ritenuto
	data.append({
		"room_charge_percentage": "Ritenuta 20%",
		"doctor_amount": ritenuta_amount
	})

	#total
	data.append({
		"room_charge_percentage": "<b>" + _("Total") + "</b>",
		"doctor_amount": grand_total_doctor_amount - ritenuta_amount
	})	

	return data
