import frappe

from erpnext.accounts.party import complete_contact_details, get_default_price_list
from erpnext.tests.utils import ERPNextTestSuite


class PartyTestCase(ERPNextTestSuite):
	def test_get_default_price_list_should_return_none_for_invalid_group(self):
		customer = frappe.get_doc(
			{
				"doctype": "Customer",
				"customer_name": "test customer",
			}
		).insert(ignore_permissions=True, ignore_mandatory=True)
		customer.customer_group = None
		customer.save()
		price_list = get_default_price_list(customer)
		assert price_list is None

	def test_complete_contact_details_handles_missing_contact(self):
		# Stale references to a non-existent Contact (e.g. set via direct DB write or
		# a server script writing a display name into contact_person) used to crash
		# with AttributeError: 'NoneType' object has no attribute 'items' because
		# frappe.db.get_value returns None for an unknown name.
		party_details = frappe._dict(
			party_type="Customer",
			party="_Test Customer",
			contact_person="non-existent-contact-xyz",
		)
		complete_contact_details(party_details)
		self.assertIsNone(party_details.contact_person)
		self.assertIsNone(party_details.contact_display)
		self.assertIsNone(party_details.contact_email)
		self.assertIsNone(party_details.contact_mobile)
		self.assertIsNone(party_details.contact_phone)
		self.assertIsNone(party_details.contact_designation)
		self.assertIsNone(party_details.contact_department)
