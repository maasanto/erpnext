import frappe
from frappe.contacts.doctype.contact.contact import Contact

# Read-only fields on the party that are `fetch_from` its primary contact.
# Supplier has no first_name/last_name field, so its mapping is a subset of Customer's.
PARTY_PRIMARY_CONTACT_FIELDS = {
	"Customer": {
		"link_fieldname": "customer_primary_contact",
		"fetched_fields": ("first_name", "last_name", "email_id", "mobile_no"),
	},
	"Supplier": {
		"link_fieldname": "supplier_primary_contact",
		"fetched_fields": ("email_id", "mobile_no"),
	},
}


class ERPNextContact(Contact):
	def on_update(self):
		"""
		After a Contact is updated, refresh the fetched contact details on any
		Customer/Supplier that uses it as their primary contact.

		The party's name/email/mobile fields are `fetch_from` the primary contact,
		so they only refresh when the link field changes - not when the linked
		Contact itself is edited. This mirrors `ERPNextAddress.on_update`, which
		does the same for the primary address.
		"""

		if hasattr(super(), "on_update"):
			super().on_update()

		self.update_party_primary_contact_details()

	def update_party_primary_contact_details(self):
		for doctype, config in PARTY_PRIMARY_CONTACT_FIELDS.items():
			parties = frappe.get_all(doctype, filters={config["link_fieldname"]: self.name}, pluck="name")
			if not parties:
				continue

			values = {fieldname: self.get(fieldname) for fieldname in config["fetched_fields"]}
			for party in parties:
				frappe.db.set_value(doctype, party, values)
