from odoo import fields, models


class BbbbeeProcurementRecommendation(models.Model):
    _name = "bbbbee.procurement.recommendation"
    _description = "B-BBEE Procurement Recommendation"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(required=True)
    current_supplier_id = fields.Many2one("res.partner", required=True)
    current_recognition_percentage = fields.Float()
    alternative_supplier_id = fields.Many2one("res.partner")
    alternative_recognition_percentage = fields.Float()
    estimated_score_impact = fields.Float()
    price_impact = fields.Monetary()
    currency_id = fields.Many2one("res.currency", default=lambda self: self.env.company.currency_id)
    state = fields.Selection([("new", "New"), ("accepted", "Accepted"), ("dismissed", "Dismissed")], default="new")
    dismissal_reason = fields.Text()
