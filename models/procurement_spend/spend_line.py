from odoo import api, fields, models
from odoo.exceptions import ValidationError


class BbbbeeSpendLine(models.Model):
    _name = "bbbbee.spend.line"
    _description = "B-BBEE Procurement Spend Line"
    _order = "invoice_date desc, id desc"

    batch_id = fields.Many2one("bbbbee.spend.batch", required=True, ondelete="cascade")
    partner_id = fields.Many2one("res.partner", required=True)
    move_id = fields.Many2one("account.move", string="Source Transaction", readonly=True)
    invoice_date = fields.Date()
    untaxed_amount = fields.Monetary()
    excluded_amount = fields.Monetary(default=0.0)
    included_amount = fields.Monetary(compute="_compute_amounts", store=True)
    recognition_percentage = fields.Float(default=0.0)
    recognised_amount = fields.Monetary(compute="_compute_amounts", store=True)
    evidence_status = fields.Selection(
        [("valid", "Valid"), ("missing", "Missing"), ("expired", "Expired"), ("review_required", "Review Required")],
        default="review_required",
    )
    evidence_status_badge_html = fields.Html(compute="_compute_evidence_status_badge_html", sanitize=False)
    classification = fields.Selection(
        [("included", "Included"), ("excluded", "Excluded"), ("review", "Review Required")],
        default="included",
    )
    currency_id = fields.Many2one(related="batch_id.currency_id")

    @api.depends("untaxed_amount", "excluded_amount", "recognition_percentage", "classification")
    def _compute_amounts(self):
        for line in self:
            line.included_amount = 0.0 if line.classification == "excluded" else line.untaxed_amount - line.excluded_amount
            line.recognised_amount = line.included_amount * (line.recognition_percentage / 100.0)

    @api.constrains("recognition_percentage")
    def _check_recognition_percentage(self):
        for line in self:
            if line.recognition_percentage < 0.0 or line.recognition_percentage > 135.0:
                raise ValidationError("Recognition percentage must be between 0 and 135.")

    @api.constrains("excluded_amount", "untaxed_amount", "classification")
    def _check_excluded_amount(self):
        for line in self:
            untaxed_abs = abs(line.untaxed_amount or 0.0)
            if line.classification != "excluded" and line.excluded_amount > untaxed_abs:
                raise ValidationError("Excluded amount cannot be greater than untaxed amount for included/review lines.")

    @api.depends("evidence_status")
    def _compute_evidence_status_badge_html(self):
        state_map = {
            "valid": ("#eef7ef", "#166534", "Valid"),
            "missing": ("#fff4f4", "#991b1b", "Missing"),
            "expired": ("#fdecec", "#991b1b", "Expired"),
            "review_required": ("#fcf6e8", "#7c5c1d", "Review Required"),
        }
        for line in self:
            bg, fg, label = state_map.get(line.evidence_status or "review_required")
            line.evidence_status_badge_html = (
                '<span class="badge badge-pill bbbbee-pill-badge" style="background:%s;color:%s;display:inline-flex;'
                'align-items:center;justify-content:center;min-width:106px;padding:4px 10px;border-radius:999px;'
                'font-size:11px;font-weight:700;letter-spacing:0.02em;text-transform:uppercase;">%s</span>'
                % (bg, fg, label)
            )
