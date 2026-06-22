from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

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
        policy = self.env["bbbbee.supplier.status.policy"]
        for move in self:
            profile = Profile.search([("partner_id", "=", move.partner_id.id)], limit=1) if move.partner_id else Profile.browse()
            move.bbbbee_profile_id = profile.id if profile else False
            move.bbbbee_warning = move.partner_id and policy.get_purchase_warning(move.partner_id) or False
