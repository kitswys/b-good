from odoo.tests.common import TransactionCase


class TestEvidencePack(TransactionCase):
    def test_generate_evidence_pack_wizard_creates_pack(self):
        period = self.env["bbbbee.measurement.period"].create(
            {
                "name": "FY2026",
                "date_start": "2026-01-01",
                "date_end": "2026-12-31",
            }
        )
        wizard = self.env["bbbbee.generate.evidence.pack.wizard"].create({"measurement_period_id": period.id})
        action = wizard.action_generate()

        self.assertEqual(action["res_model"], "bbbbee.evidence.pack")
