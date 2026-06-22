from odoo import api, fields, models
from odoo.exceptions import UserError


class BbbbeeImportSpendWizard(models.TransientModel):
    _name = "bbbbee.import.spend.wizard"
    _description = "Import B-BBEE Procurement Spend"

    measurement_period_id = fields.Many2one("bbbbee.measurement.period", required=True)
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company, required=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["company_id"] = self.env.company.id
        return super().create(vals_list)

    def action_import(self):
        period = self.measurement_period_id
        if period.company_id != self.company_id:
            raise UserError("Selected measurement period does not belong to the selected company.")
        accounting = self.env["bbbbee.odoo.accounting.adapter"]
        classifier = self.env["bbbbee.spend.classifier"]
        batch = self.env["bbbbee.spend.batch"].create(
            {
                "name": "Spend Import - %s" % period.name,
                "measurement_period_id": period.id,
                "company_id": self.company_id.id,
            }
        )
        moves = accounting.get_posted_vendor_moves(period.date_start, period.date_end, self.company_id)
        for move in moves:
            profile = self.env["bbbbee.supplier.profile"].search([("partner_id", "=", move.partner_id.id)], limit=1)
            compliance_status = profile.compliance_status if profile else "missing"
            evidence_status = {
                "valid": "valid",
                "expiring_soon": "review_required",
                "expired": "expired",
                "missing": "missing",
                "superseded": "review_required",
            }.get(compliance_status, "review_required")
            amount = abs(move.amount_untaxed or 0.0)
            if move.move_type == "in_refund":
                amount = -amount
            self.env["bbbbee.spend.line"].create(
                {
                    "batch_id": batch.id,
                    "partner_id": move.partner_id.id,
                    "move_id": move.id,
                    "invoice_date": move.invoice_date,
                    "untaxed_amount": amount,
                    "excluded_amount": 0.0,
                    "recognition_percentage": profile.recognition_percentage if profile else 0.0,
                    "classification": classifier.classify_move(move),
                    "evidence_status": evidence_status,
                }
            )
        if moves:
            batch.write({"state": "review"})
        return {
            "type": "ir.actions.act_window",
            "res_model": "bbbbee.spend.batch",
            "res_id": batch.id,
            "view_mode": "form",
            "target": "current",
        }
