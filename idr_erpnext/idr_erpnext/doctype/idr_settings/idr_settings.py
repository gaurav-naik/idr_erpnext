# -*- coding: utf-8 -*-
# Copyright (c) 2018, Massimiliano Corvino and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _

class IDRSettings(Document):
	pass

def get_idr_fee_rate(procedure_type, physician_category):
	try:
		return frappe.db.get_value("IDR Settings Procedure Type Rate", {"procedure_type":procedure_type, "physician_category":physician_category}, "rate")
	except Exception as e:
		frappe.throw(_("Check Procedure Type and Physician Category"))
	