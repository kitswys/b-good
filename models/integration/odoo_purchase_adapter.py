from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    bbbbee_profile_id = fields.Many2one(
        "bbbbee.supplier.profile",
        compute="_compute_bbbbee_compliance",
        string="B-BBEE Profile",
    )
    bbbbee_level = fields.Selection(
        related="bbbbee_profile_id.bbbbee_level",
        string="B-BBEE Level",
        readonly=True,
    )
    bbbbee_recognition_percentage = fields.Float(
        related="bbbbee_profile_id.recognition_percentage",
        string="Recognition %",
        readonly=True,
    )
    bbbbee_compliance_status = fields.Selection(
        related="bbbbee_profile_id.compliance_status",
        string="Compliance Status",
        readonly=True,
    )
    bbbbee_warning = fields.Char(compute="_compute_bbbbee_compliance")

    @api.depends("partner_id")
    def _compute_bbbbee_compliance(self):
        Profile = self.env["bbbbee.supplier.profile"]
        for order in self:
            order.bbbbee_profile_id = (
                Profile.search([("partner_id", "=", order.partner_id.id)], limit=1).id if order.partner_id else False
            )
            order.bbbbee_warning = order.partner_id and self.env["bbbbee.supplier.status.policy"].get_purchase_warning(order.partner_id) or False
