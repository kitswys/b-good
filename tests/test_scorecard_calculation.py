from odoo.tests.common import TransactionCase


class TestScorecardCalculation(TransactionCase):
    def test_scorecard_calculates_shortfall(self):
        rule_set = self.env["bbbbee.scorecard.rule.set"].create(
            {
                "name": "Rule Set",
                "effective_date": "2026-01-01",
                "target_percentage": 80.0,
                "available_points": 25.0,
            }
        )
        period = self.env["bbbbee.measurement.period"].create(
            {
                "name": "FY2026",
                "date_start": "2026-01-01",
                "date_end": "2026-12-31",
                "active_rule_set_id": rule_set.id,
            }
        )
        batch = self.env["bbbbee.spend.batch"].create({"name": "Batch", "measurement_period_id": period.id})
        supplier = self.env["res.partner"].create({"name": "Supplier", "supplier_rank": 1})
        self.env["bbbbee.spend.line"].create(
            {
                "batch_id": batch.id,
                "partner_id": supplier.id,
                "untaxed_amount": 100.0,
                "recognition_percentage": 50.0,
            }
        )
        assessment = self.env["bbbbee.scorecard.assessment"].create(
            {
                "name": "Assessment",
                "measurement_period_id": period.id,
                "rule_set_id": rule_set.id,
                "spend_batch_ids": [(6, 0, batch.ids)],
            }
        )

        self.assertEqual(assessment.shortfall_amount, 30.0)
