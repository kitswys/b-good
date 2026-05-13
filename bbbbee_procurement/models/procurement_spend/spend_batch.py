from odoo import api, fields, models


class BbbbeeSpendBatch(models.Model):
    _name = "bbbbee.spend.batch"
    _description = "B-BBEE Procurement Spend Batch"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(required=True, tracking=True)
    measurement_period_id = fields.Many2one("bbbbee.measurement.period", required=True)
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company, required=True)
    line_ids = fields.One2many("bbbbee.spend.line", "batch_id")
    total_included_amount = fields.Monetary(compute="_compute_totals", store=True)
    total_recognised_amount = fields.Monetary(compute="_compute_totals", store=True)
    currency_id = fields.Many2one(related="company_id.currency_id")
    state = fields.Selection(
        [("draft", "Draft"), ("review", "In Review"), ("locked", "Locked"), ("superseded", "Superseded")],
        default="draft",
        tracking=True,
    )

    @api.depends("line_ids.included_amount", "line_ids.recognised_amount")
    def _compute_totals(self):
        for batch in self:
            batch.total_included_amount = sum(batch.line_ids.mapped("included_amount"))
            batch.total_recognised_amount = sum(batch.line_ids.mapped("recognised_amount"))

    def action_lock(self):
        self.write({"state": "locked"})
