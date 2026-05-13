from odoo.tests.common import TransactionCase


class TestRecognisedSpend(TransactionCase):
    def test_recognised_spend_uses_recognition_percentage(self):
        period = self.env["bbbbee.measurement.period"].create(
            {
                "name": "FY2026",
                "date_start": "2026-01-01",
                "date_end": "2026-12-31",
            }
        )
        batch = self.env["bbbbee.spend.batch"].create({"name": "Batch", "measurement_period_id": period.id})
        supplier = self.env["res.partner"].create({"name": "Supplier", "supplier_rank": 1})
        line = self.env["bbbbee.spend.line"].create(
            {
                "batch_id": batch.id,
                "partner_id": supplier.id,
                "untaxed_amount": 100000.0,
                "recognition_percentage": 125.0,
            }
        )

        self.assertEqual(line.recognised_amount, 125000.0)
