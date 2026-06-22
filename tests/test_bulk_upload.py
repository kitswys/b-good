from odoo.tests.common import TransactionCase


class TestBulkUpload(TransactionCase):
    def test_bulk_upload_creates_certificate(self):
        partner = self.env["res.partner"].create({"name": "Bulk Supplier", "supplier_rank": 1})
        profile = self.env["bbbbee.supplier.profile"].create({"partner_id": partner.id})
        tag = self.env["bbbbee.document.tag"].create({"name": "CIPC", "usage": "certificate"})

        wizard = self.env["bbbbee.certificate.bulk.upload.wizard"].create(
            {
                "profile_id": profile.id,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "certificate_type": "certificate",
                            "certificate_number": "BULK-001",
                            "expiry_date": "2026-12-31",
                            "tag_ids": [(6, 0, [tag.id])],
                        },
                    )
                ],
            }
        )
        wizard.action_create_documents()

        certificate = self.env["bbbbee.supplier.certificate"].search([("certificate_number", "=", "BULK-001")], limit=1)
        self.assertTrue(certificate)
        self.assertEqual(certificate.profile_id, profile)
        self.assertIn(tag, certificate.tag_ids)
