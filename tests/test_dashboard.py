from odoo.tests.common import TransactionCase


class TestDashboard(TransactionCase):
    def test_dashboard_summarises_current_data(self):
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
        partner = self.env["res.partner"].create({"name": "Supplier", "supplier_rank": 1})
        profile = self.env["bbbbee.supplier.profile"].create({"partner_id": partner.id, "recognition_percentage": 100.0})
        self.env["bbbbee.supplier.certificate"].create(
            {
                "profile_id": profile.id,
                "expiry_date": "2026-12-31",
                "attachment_id": False,
            }
        )
        batch = self.env["bbbbee.spend.batch"].create({"name": "Batch", "measurement_period_id": period.id})
        self.env["bbbbee.spend.line"].create(
            {
                "batch_id": batch.id,
                "partner_id": partner.id,
                "untaxed_amount": 100.0,
                "recognition_percentage": 100.0,
                "classification": "included",
                "evidence_status": "missing",
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

        dashboard = self.env["bbbbee.dashboard.wizard"].create({"measurement_period_id": period.id})

        self.assertEqual(dashboard.spend_batch_count, 1)
        self.assertEqual(dashboard.missing_evidence_count, 1)
        self.assertEqual(dashboard.recognised_procurement_spend, assessment.recognised_procurement_spend)
