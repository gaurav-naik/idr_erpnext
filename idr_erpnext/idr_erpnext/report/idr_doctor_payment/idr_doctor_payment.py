# Copyright (c) 2013, Massimiliano Corvino and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	columns, data = get_columns(), get_data2(filters)
	return columns, data

def get_columns():
	return [
		{
			"fieldname": "date",
			"label": _("Data"),
			"fieldtype": "Date",
			"width": 90
		},
		{
			"fieldname": "patient_name",
			"label": _("Nominativo Paziente"),
			"fieldtype": "Data",
			"width": 220
		},
		{
			"fieldname": "payment_amount",
			"label": _("Importo Pagato"),
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"fieldname": "expenses",
			"label": _("Spese"),
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"fieldname": "room_charge_percentage",
			"label": _("% Studio"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "room_charge_amount",
			"label": _("Importo Studio"),
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"fieldname": "doctor_amount",
			"label": _("Importo Medico + Spese"),
			"fieldtype": "Currency",
			"width": 200
		},
	]

def get_data2(filters): ### [WIP]
	if len(frappe.get_all("IDR Physician Fee", {"physician":filters.get("physician")})) == 0:
		frappe.throw(_("Please set physician fees for this doctor"))

	data = []
	invoices = frappe.get_all("Sales Invoice", 
		filters={
			"posting_date": ("between", [filters.get("from_date"), filters.get("to_date")]), 
			"idr_physician":filters.get("physician"),
			"docstatus": 1
		},
		fields=["*"],
		order_by="posting_date")

	for invoice in invoices:
		row = {"date": invoice.posting_date}

		patient_name = ""
		if invoice.appointment:
			patient_name = frappe.db.get_value("Patient Appointment", invoice.appointment, "patient_name")

		row["patient_name"] = patient_name

		physician_dept = frappe.db.get_value("Physician", invoice.idr_physician, "department")
		invoice_items = frappe.get_all("Sales Invoice Item", filters={"parent": invoice.name}, fields=["*"])

		expenses_per_item = (float(invoice.idr_expenses or 0.0)) / len(invoice_items)

		invoice_idr_fees, invoice_physician_amount = 0, 0
		physician_fee_percentage_list = []
		for item in invoice_items:
			physician_fee_percentage = frappe.db.get_value("IDR Physician Fee", 
				filters={"service_category": item.item_group, "physician":invoice.idr_physician}, fieldname="rate")

			item_rate = item.rate - expenses_per_item
			item_idr_fees = (item_rate * (physician_fee_percentage/100))
			physician_amount = item.rate - item_idr_fees
			
			invoice_idr_fees += item_idr_fees
			invoice_physician_amount += (physician_amount)

			physician_fee_percentage_list.append(str(physician_fee_percentage))

		row["payment_amount"] = invoice.net_total
		row["expenses"] = invoice.idr_expenses
		row["room_charge_percentage"] = " + ".join(physician_fee_percentage_list)
		row["room_charge_amount"] = invoice_idr_fees
		row["doctor_amount"] = invoice_physician_amount

		data.append(row)
	return data

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
			"physician":filters.get("physician"), "sales_invoice":("!=", ""), "docstatus":1}, 
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

			rate = 100-(total_physician_rate*100/total_selling_rate)
			procedure_type_fee_rates.append(str(rate))

		row["payment_amount"] = total_selling_rate
		row["expenses"] = appointment.idr_extra_expenses
		row["room_charge_percentage"] = " + ".join(procedure_type_fee_rates)
		row["room_charge_amount"] = total_selling_rate - total_physician_rate
		row["doctor_amount"] = total_physician_rate

		data.append(row)

	#grand totals

	grand_total_doctor_amount = sum([data_row.get("doctor_amount") for data_row in data])
	ritenuta_amount = grand_total_doctor_amount * 0.2 #@20%

	data.append({
		"nominativo_paziente": _("Totale"),
		"expenses": sum([data_row.get("expenses") for data_row in data]),
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
