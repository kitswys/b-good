from odoo import api, fields, models
from odoo.exceptions import ValidationError


class BbbbeeMeasurementPeriod(models.Model):
    _name = "bbbbee.measurement.period"
    _description = "B-BBEE Measurement Period"

    name = fields.Char(required=True, help="Friendly label for the compliance period, e.g. FY2026.")
    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.company,
        required=True,
        help="Company this period applies to.",
    )
    date_start = fields.Date(required=True, help="Start date of the measurement period.")
    date_end = fields.Date(required=True, help="End date of the measurement period.")
    active_rule_set_id = fields.Many2one(
        "bbbbee.scorecard.rule.set",
        help="Rule set used to calculate targets, points, and shortfall for this period.",
    )
    active = fields.Boolean(default=True, help="Inactive periods are hidden from normal operations.")

    @api.constrains("date_start", "date_end")
    def _check_date_range(self):
        for period in self:
            if period.date_start and period.date_end and period.date_end < period.date_start:
                raise ValidationError("Measurement period end date must be on or after the start date.")

    @api.constrains("date_start", "date_end", "company_id")
    def _check_overlap(self):
        for period in self:
            if not period.date_start or not period.date_end:
                continue
            overlap_count = self.search_count(
                [
                    ("id", "!=", period.id),
                    ("company_id", "=", period.company_id.id),
                    ("date_start", "<=", period.date_end),
                    ("date_end", ">=", period.date_start),
                ]
            )
            if overlap_count:
                raise ValidationError("Measurement periods for the same company cannot overlap.")

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
