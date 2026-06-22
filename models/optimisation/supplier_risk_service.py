from odoo import models


class BbbbeeSupplierRiskService(models.AbstractModel):
    _name = "bbbbee.supplier.risk.service"
    _description = "Supplier Risk Service"

    def get_risk_level(self, partner):
        profile = self.env["bbbbee.supplier.profile"].search([("partner_id", "=", partner.id)], limit=1)
        if not profile or profile.compliance_status in ("missing", "expired"):
            return "high"
        if profile.compliance_status == "expiring_soon" or profile.recognition_percentage < 80:
            return "medium"
        return "low"
