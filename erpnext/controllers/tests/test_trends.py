import frappe
from frappe import _
from frappe.desk.query_report import run

from erpnext.accounts.doctype.sales_invoice.test_sales_invoice import create_sales_invoice
from erpnext.tests.utils import ERPNextTestSuite

TRENDS_REPORTS = (
	"Delivery Note Trends",
	"Purchase Invoice Trends",
	"Purchase Order Trends",
	"Purchase Receipt Trends",
	"Quotation Trends",
	"Sales Invoice Trends",
	"Sales Order Trends",
)


class TestTrends(ERPNextTestSuite):
	def test_report_total_row_is_the_only_total(self):
		create_sales_invoice(item="_Test Item", qty=2, rate=100, posting_date="2026-06-01")
		filters = {
			"company": "_Test Company",
			"fiscal_year": "_Test Fiscal Year 2026",
			"based_on": "Item",
			"period": "Yearly",
		}

		for report in TRENDS_REPORTS:
			with self.subTest(report=report):
				# Sites installed before the reports built their own total row still have this on.
				frappe.db.set_value("Report", report, "add_total_row", 1)

				response = run(report, filters=filters, ignore_prepared_report=True)

				self.assertFalse(response["add_total_row"])
				*item_rows, total_row = response["result"]
				self.assertEqual(total_row["item"], f"'{_('Total')}'")
				self.assertEqual(total_row["total(amt)"], sum(row["total(amt)"] for row in item_rows))
