from odoo import fields, models


class BbbbeeMeasurementPeriod(models.Model):
    _name = "bbbbee.measurement.period"
    _description = "B-BBEE Measurement Period"

    name = fields.Char(required=True)
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company, required=True)
    date_start = fields.Date(required=True)
    date_end = fields.Date(required=True)
    active_rule_set_id = fields.Many2one("bbbbee.scorecard.rule.set")
    active = fields.Boolean(default=True)
