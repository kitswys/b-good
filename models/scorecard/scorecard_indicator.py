from odoo import fields, models


class BbbbeeScorecardIndicator(models.Model):
    _name = "bbbbee.scorecard.indicator"
    _description = "B-BBEE Scorecard Indicator"

    name = fields.Char(required=True)
    rule_set_id = fields.Many2one("bbbbee.scorecard.rule.set", required=True, ondelete="cascade")
    target_percentage = fields.Float()
    available_points = fields.Float()
