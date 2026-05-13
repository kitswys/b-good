from odoo import api, fields, models


class BbbbeeScorecardAssessment(models.Model):
    _name = "bbbbee.scorecard.assessment"
    _description = "B-BBEE Procurement Scorecard Assessment"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(required=True)
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company, required=True)
    measurement_period_id = fields.Many2one("bbbbee.measurement.period", required=True)
    rule_set_id = fields.Many2one("bbbbee.scorecard.rule.set", required=True)
    spend_batch_ids = fields.Many2many("bbbbee.spend.batch")
    total_measured_spend = fields.Monetary(compute="_compute_score", store=True)
    recognised_procurement_spend = fields.Monetary(compute="_compute_score", store=True)
    target_percentage = fields.Float(related="rule_set_id.target_percentage", store=True)
    achieved_percentage = fields.Float(compute="_compute_score", store=True)
    available_points = fields.Float(related="rule_set_id.available_points", store=True)
    actual_points = fields.Float(compute="_compute_score", store=True)
    shortfall_amount = fields.Monetary(compute="_compute_score", store=True)
    currency_id = fields.Many2one(related="company_id.currency_id")
    state = fields.Selection(
        [("draft", "Draft"), ("calculated", "Calculated"), ("approved", "Approved"), ("frozen", "Frozen")],
        default="draft",
        tracking=True,
    )

    @api.depends(
        "spend_batch_ids.total_included_amount",
        "spend_batch_ids.total_recognised_amount",
        "target_percentage",
        "available_points",
    )
    def _compute_score(self):
        for assessment in self:
            measured = sum(assessment.spend_batch_ids.mapped("total_included_amount"))
            recognised = sum(assessment.spend_batch_ids.mapped("total_recognised_amount"))
            target_amount = measured * (assessment.target_percentage / 100.0)
            achieved = (recognised / measured * 100.0) if measured else 0.0
            assessment.total_measured_spend = measured
            assessment.recognised_procurement_spend = recognised
            assessment.achieved_percentage = achieved
            assessment.actual_points = min(assessment.available_points, assessment.available_points * achieved / assessment.target_percentage) if assessment.target_percentage else 0.0
            assessment.shortfall_amount = max(0.0, target_amount - recognised)

    def action_recalculate(self):
        self._compute_score()
        self.write({"state": "calculated"})
