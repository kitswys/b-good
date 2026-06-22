from datetime import timedelta

from odoo import fields
from odoo.tests.common import TransactionCase


class TestCertificateExpiry(TransactionCase):
    def test_certificate_without_attachment_is_missing(self):
        partner = self.env["res.partner"].create({"name": "Test Supplier", "supplier_rank": 1})
        profile = self.env["bbbbee.supplier.profile"].create({"partner_id": partner.id})
        certificate = self.env["bbbbee.supplier.certificate"].create(
            {
                "profile_id": profile.id,
                "expiry_date": fields.Date.today() + timedelta(days=365),
            }
        )

        self.assertEqual(certificate.state, "missing")
