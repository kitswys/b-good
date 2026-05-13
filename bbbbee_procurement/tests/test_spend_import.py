from odoo.tests.common import TransactionCase


class TestSpendImport(TransactionCase):
    def test_import_wizard_creates_batch(self):
        period = self.env["bbbbee.measurement.period"].create(
            {
                "name": "FY2026",
                "date_start": "2026-01-01",
                "date_end": "2026-12-31",
            }
        )
        wizard = self.env["bbbbee.import.spend.wizard"].create({"measurement_period_id": period.id})
        action = wizard.action_import()

        self.assertEqual(action["res_model"], "bbbbee.spend.batch")
