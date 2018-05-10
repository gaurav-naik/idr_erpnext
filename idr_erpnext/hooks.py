# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "idr_erpnext"
app_title = "IDR ERPNext"
app_publisher = "Massimiliano Corvino"
app_description = "ERPNext customization for IDR"
app_icon = "fa fa-stethoscope"
app_color = "green"
app_email = "massimiliano.corvino@gmail.com"
app_license = "GPL v3"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/idr_erpnext/css/idr_erpnext.css"
# app_include_js = "/assets/idr_erpnext/js/idr_erpnext.js"

# include js, css files in header of web template
# web_include_css = "/assets/idr_erpnext/css/idr_erpnext.css"
# web_include_js = "/assets/idr_erpnext/js/idr_erpnext.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
doctype_list_js = {
	"Patient Appointment" : "public/js/patient_appointment_list.js"
}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "idr_erpnext.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "idr_erpnext.install.before_install"
# after_install = "idr_erpnext.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "idr_erpnext.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Patient": {
		"on_update": "idr_erpnext.api.patient_on_update"
	},
	"Physician": {
		"after_insert": "idr_erpnext.api.physician_after_insert"
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"idr_erpnext.tasks.all"
# 	],
# 	"daily": [
# 		"idr_erpnext.tasks.daily"
# 	],
# 	"hourly": [
# 		"idr_erpnext.tasks.hourly"
# 	],
# 	"weekly": [
# 		"idr_erpnext.tasks.weekly"
# 	]
# 	"monthly": [
# 		"idr_erpnext.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "idr_erpnext.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
override_whitelisted_methods = {
	"erpnext.healthcare.doctype.patient_appointment.patient_appointment.get_availability_data":"idr_erpnext.api.idr_get_availability_data",
	"erpnext.healthcare.doctype.patient_appointment.patient_appointment.create_invoice":"idr_erpnext.api.idr_create_invoice"
}

fixtures =  [
	{"dt":"Custom Field", "filters": [["name", "in", [
		"Patient-idr_sb_patient_quick_entry",
		"Patient-idr_patient_first_name",
		"Patient-idr_patient_last_name",
		"Patient-idr_cb_patient_quick_entry",
		"Patient-idr_patient_phone_no",
		"Patient Appointment-idr_appointment_type",
		"Physician-idr_supplier",
		"Customer-idr_customer_quick_entry",
		"Customer-idr_customer_first_name",
		"Customer-idr_customer_last_name",
		"Customer-idr_customer_gender",
		"Customer-idr_customer_cb_1",
		"Customer-idr_customer_date_of_birth",
		"Customer-idr_customer_place_of_birth",
		"Customer-idr_customer_tax_id",
		"Physician Schedule-idr_schedule_type",
		"Physician Schedule Time Slot-idr_date",
		"Customer-idr_codice_fiscale_buttons",
		"Purchase Invoice Item-idr_sb_patient_appointment",
		"Purchase Invoice Item-idr_patient_appointment",
		"Purchase Invoice Item-idr_patient_appointment_invoice",
		"Sales Invoice-diagnosi",
		"Sales Invoice-diagnosi_section",
		"Patient Appointment-idr_servizio"
	]]]},
	{"dt":"Property Setter", "filters": [["name", "in", [
		"Patient-sex-default",
		"Sales Invoice-default_print_format",
		"Physician-department-in_list_view",
		"Patient Appointment-appointment_date-in_list_view",
		"Customer-customer_type-default",
		"Customer-basic_info-collapsible",
		"Customer-basic_info-collapsible_depends_on",
		"Patient Appointment-title_field",
		"Patient Appointment-patient-in_list_view",
		"Patient Appointment-appointment_time-in_list_view",
		"Patient Appointment-status-in_list_view",
		"Sales Invoice-project-hidden",
		"Sales Invoice-is_pos-hidden",
		"Sales Invoice-read_only_onload",
		"Patient Appointment-read_only_onload"
	]]]},
	{"dt":"Print Format", "filters": [["name", "in", [
		"Consent Letter", 
		"Medical Certificate",
		"IDR Fattura Paziente"
	]]]},
	{"dt":"Letter Head", "filters": [["name", "in", [
		"IDR"
	]]]},
	{"dt":"Calendar View", "filters": [["name", "in", [
		"IDR Patient Appointment"
	]]]},
	{"dt":"Report", "filters": [["name", "in", [
		"Lista Appuntamenti"
	]]]}
]
