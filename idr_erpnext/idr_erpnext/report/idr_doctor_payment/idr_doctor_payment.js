// Copyright (c) 2016, Massimiliano Corvino and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["IDR Doctor Payment"] = {
	"filters": [
		{
			"fieldname":"physician",
			"label": __("Doctor"),
			"fieldtype": "Link",
			"options": "Physician",
			"reqd": 1
		},
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"reqd": 1
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"reqd": 1
		},
	]
};
