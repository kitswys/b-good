from odoo.tests.common import TransactionCase


class TestSupplierCompliance(TransactionCase):
    def test_profile_defaults_to_missing_without_certificate(self):
        partner = self.env["res.partner"].create({"name": "Test Supplier", "supplier_rank": 1})
        profile = self.env["bbbbee.supplier.profile"].create({"partner_id": partner.id})

        self.assertEqual(profile.compliance_status, "missing")
