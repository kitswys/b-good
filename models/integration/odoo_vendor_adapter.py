from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    bbbbee_profile_id = fields.One2many("bbbbee.supplier.profile", "partner_id", string="B-BBEE Profile")
