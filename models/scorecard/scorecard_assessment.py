from odoo import api, fields, models
from odoo.exceptions import ValidationError


class BbbbeeScorecardAssessment(models.Model):
    _name = "bbbbee.scorecard.assessment"
    _description = "B-BBEE Procurement Scorecard Assessment"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(required=True)
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company, required=True)
    measurement_period_id = fields.Many2one("bbbbee.measurement.period", required=True, ondelete="cascade")
    rule_set_id = fields.Many2one("bbbbee.scorecard.rule.set", required=True, ondelete="restrict")
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
    state_badge_html = fields.Html(compute="_compute_state_badge_html", sanitize=False)

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

    def action_approve(self):
        self.write({"state": "approved"})

    def action_freeze(self):
        self.write({"state": "frozen"})

    def action_reset_to_draft(self):
        self.write({"state": "draft"})

    @api.depends("state")
    def _compute_state_badge_html(self):
        state_map = {
            "draft": ("#fff4f4", "#991b1b", "Draft"),
            "calculated": ("#fcf6e8", "#7c5c1d", "Calculated"),
            "approved": ("#eef7ef", "#166534", "Approved"),
            "frozen": ("#f3f4f6", "#475569", "Frozen"),
        }
        for assessment in self:
            bg, fg, label = state_map.get(assessment.state or "draft")
            assessment.state_badge_html = (
                '<span class="badge badge-pill bbbbee-pill-badge" style="background:%s;color:%s;display:inline-flex;'
                'align-items:center;justify-content:center;min-width:96px;padding:4px 10px;border-radius:999px;'
                'font-size:11px;font-weight:700;letter-spacing:0.02em;text-transform:uppercase;">%s</span>'
                % (bg, fg, label)
            )

    @api.constrains("measurement_period_id", "spend_batch_ids")
    def _check_batches_match_period(self):
        for assessment in self:
            mismatched = assessment.spend_batch_ids.filtered(
                lambda batch: batch.measurement_period_id != assessment.measurement_period_id
            )
            if mismatched:
                raise ValidationError("All linked spend batches must belong to the selected measurement period.")

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
