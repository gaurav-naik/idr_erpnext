frappe.ui.form.on("Patient Appointment", {
});

frappe.ui.keys.on("shift+c", function(e) {
	frappe.click_button("Check availability")
})
