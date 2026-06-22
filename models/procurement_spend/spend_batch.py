from odoo import api, fields, models
from odoo.exceptions import ValidationError


class BbbbeeSpendBatch(models.Model):
    _name = "bbbbee.spend.batch"
    _description = "B-BBEE Procurement Spend Batch"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(required=True, tracking=True)
    measurement_period_id = fields.Many2one("bbbbee.measurement.period", required=True, ondelete="cascade")
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company, required=True, readonly=True)
    line_ids = fields.One2many("bbbbee.spend.line", "batch_id")
    total_included_amount = fields.Monetary(compute="_compute_totals", store=True)
    total_recognised_amount = fields.Monetary(compute="_compute_totals", store=True)
    currency_id = fields.Many2one(related="company_id.currency_id")
    state = fields.Selection(
        [("draft", "Draft"), ("review", "In Review"), ("locked", "Locked"), ("superseded", "Superseded")],
        default="draft",
        tracking=True,
    )
    state_badge_html = fields.Html(compute="_compute_state_badge_html", sanitize=False)

    @api.depends("line_ids.included_amount", "line_ids.recognised_amount")
    def _compute_totals(self):
        for batch in self:
            batch.total_included_amount = sum(batch.line_ids.mapped("included_amount"))
            batch.total_recognised_amount = sum(batch.line_ids.mapped("recognised_amount"))

    def action_lock(self):
        self.write({"state": "locked"})

    def action_set_review(self):
        self.write({"state": "review"})

    def action_reset_to_draft(self):
        self.write({"state": "draft"})

    def action_print_schedule(self):
        return self.env.ref("bbbbee_procurement.action_report_bbbbee_spend_schedule").report_action(self)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["company_id"] = self.env.company.id
        return super().create(vals_list)

    def write(self, vals):
        if "company_id" in vals:
            raise ValidationError("The company on a spend batch cannot be changed.")
        return super().write(vals)

    @api.depends("state")
    def _compute_state_badge_html(self):
        state_map = {
            "draft": ("#fff4f4", "#991b1b", "Draft"),
            "review": ("#fcf6e8", "#7c5c1d", "In Review"),
            "locked": ("#eef7ef", "#166534", "Locked"),
            "superseded": ("#f3f4f6", "#475569", "Superseded"),
        }
        for batch in self:
            bg, fg, label = state_map.get(batch.state or "draft")
            batch.state_badge_html = (
                '<span class="badge badge-pill bbbbee-pill-badge" style="background:%s;color:%s;display:inline-flex;'
                'align-items:center;justify-content:center;min-width:96px;padding:4px 10px;border-radius:999px;'
                'font-size:11px;font-weight:700;letter-spacing:0.02em;text-transform:uppercase;">%s</span>'
                % (bg, fg, label)
            )
