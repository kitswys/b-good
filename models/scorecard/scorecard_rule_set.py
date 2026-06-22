from odoo import api, fields, models


class BbbbeeScorecardRuleSet(models.Model):
    _name = "bbbbee.scorecard.rule.set"
    _description = "B-BBEE Scorecard Rule Set"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(required=True, tracking=True)
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)
    effective_date = fields.Date(required=True)
    expiry_date = fields.Date()
    target_percentage = fields.Float(default=80.0)
    available_points = fields.Float(default=25.0)
    indicator_ids = fields.One2many("bbbbee.scorecard.indicator", "rule_set_id")
    state = fields.Selection([("draft", "Draft"), ("active", "Active"), ("retired", "Retired")], default="draft")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["company_id"] = self.env.company.id
        return super().create(vals_list)

    def write(self, vals):
        if "company_id" in vals:
            vals = dict(vals)
            vals["company_id"] = self.env.company.id
        return super().write(vals)
