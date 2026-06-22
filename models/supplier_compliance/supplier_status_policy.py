from odoo import models


class BbbbeeSupplierStatusPolicy(models.AbstractModel):
    _name = "bbbbee.supplier.status.policy"
    _description = "Supplier Compliance Status Policy"

    def get_purchase_warning(self, partner):
        profile = self.env["bbbbee.supplier.profile"].search([("partner_id", "=", partner.id)], limit=1)
        if not profile or profile.compliance_status == "missing":
            return "Supplier has no verification-ready B-BBEE evidence."
        if profile.compliance_status == "expired":
            return "Supplier B-BBEE evidence has expired."
        if profile.compliance_status == "expiring_soon":
            return "Supplier B-BBEE evidence is expiring soon."
        return False
