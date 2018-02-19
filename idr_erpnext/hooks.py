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
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
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

# doc_events = {
# 	"Patient": {
# 		"after_insert": "idr_erpnext.api.patient_after_insert"
# 	}
# }

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
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "idr_erpnext.event.get_events"
# }

fixtures =  [
	{"dt":"Custom Field", "filters": [["name", "in",
												["Patient-idr_patient_address",
												"Patient-idr_patient_address_display", 
												"Patient-idr_place_of_birth",
												"Patient Appointment-idr_appointment_type"]]]},
	{"dt":"Print Format", "filters": [["name", "in", ["Consent Letter", "Medical Certificate"]]]}
]



