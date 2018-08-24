# Copyright (c) 2013, Massimiliano Corvino and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	columns, data = get_columns(), get_data(filters)
	return columns, data


def get_columns():
	return [
		{
			"fieldname": "first_name",
			"label": _("Name"),
			"fieldtype": "Data",
			"width": 90
		},
		{
			"fieldname": "last_name",
			"label": _("Surname"),
			"fieldtype": "Data",
			"width": 220
		},
		{
			"fieldname": "phone",
			"label": _("Phone"),
			"fieldtype": "Data",
			"width": 120
		},
	]

def get_data(filters):
	query = """SELECT DISTINCT idr_patient_first_name AS first_name, 
		idr_patient_last_name as last_name, phone  
		FROM `tabPatient` 
		INNER JOIN `tabPatient Appointment`  
		ON `tabPatient`.`name` = `tabPatient Appointment`.`patient`  
		WHERE `tabPatient Appointment`.physician = %(physician)s"""
	
	if filters.get("from_date") and filters.get("to_date"):
		query += """AND `tabPatient Appointment`.appointment_date BETWEEN 
		%(from_date)s AND %(to_date)s;"""
	
	
	return frappe.db.sql(query, {
		"physician": filters.get("physician"),
		"from_date": filters.get("from_date"),
		"to_date": filters.get("to_date"),
	}, as_dict = 1)


	# return frappe.db.sql("""SELECT DISTINCT idr_patient_first_name AS first_name, 
	# 	idr_patient_last_name as last_name, phone  
	# 	FROM `tabPatient` 
	# 	INNER JOIN `tabPatient Appointment`  
	# 	ON `tabPatient`.`name` = `tabPatient Appointment`.`patient`  
	# 	WHERE `tabPatient Appointment`.physician = %(physician)s  
	# 	AND `tabPatient Appointment`.appointment_date BETWEEN 
	# 	%(from_date)s AND %(to_date)s;""", 
	# 	{
	# 		"physician": filters.get("physician"),
	# 		"from_date": filters.get("from_date"),
	# 		"to_date": filters.get("to_date"),
	# 	}, as_dict = 1)

