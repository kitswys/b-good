from odoo import api, fields, models


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
