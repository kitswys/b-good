from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    bbbbee_warning = fields.Char(compute="_compute_bbbbee_warning")

    @api.depends("partner_id")
    def _compute_bbbbee_warning(self):
        policy = self.env["bbbbee.supplier.status.policy"]
        for order in self:
            order.bbbbee_warning = order.partner_id and policy.get_purchase_warning(order.partner_id) or False
