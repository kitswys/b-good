from datetime import timedelta

from odoo import fields
from odoo.tests.common import TransactionCase


class TestAlertPolicy(TransactionCase):
    def test_alert_policy_logs_due_alerts(self):
        partner = self.env["res.partner"].create({"name": "Alert Supplier", "supplier_rank": 1, "email": "supplier@example.com"})
        profile = self.env["bbbbee.supplier.profile"].create({"partner_id": partner.id})
        certificate = self.env["bbbbee.supplier.certificate"].create(
            {
                "profile_id": profile.id,
                "expiry_date": fields.Date.today() + timedelta(days=30),
                "attachment_file": "ZGVtbw==",
                "attachment_filename": "demo.txt",
            }
        )
        policy = self.env["bbbbee.compliance.alert.policy"].create(
            {
                "name": "Default",
                "company_id": self.env.company.id,
                "reminder_days": "30",
            }
        )

        policy._send_expiry_reminders()

        log = self.env["bbbbee.compliance.alert.log"].search([("certificate_id", "=", certificate.id)], limit=1)
        self.assertTrue(log)
        self.assertEqual(log.reminder_days, 30)
