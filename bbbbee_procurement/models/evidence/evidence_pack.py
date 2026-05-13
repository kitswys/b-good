from odoo import fields, models


class BbbbeeEvidencePack(models.Model):
    _name = "bbbbee.evidence.pack"
    _description = "B-BBEE Evidence Pack"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(required=True)
    measurement_period_id = fields.Many2one("bbbbee.measurement.period", required=True)
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company, required=True)
    assessment_id = fields.Many2one("bbbbee.scorecard.assessment")
    item_ids = fields.One2many("bbbbee.evidence.item", "pack_id")
    generated_on = fields.Datetime(default=fields.Datetime.now)
    version = fields.Integer(default=1)
    state = fields.Selection([("draft", "Draft"), ("generated", "Generated"), ("frozen", "Frozen")], default="draft")

    def action_freeze(self):
        self.write({"state": "frozen"})
