from odoo import fields, models
from odoo.exceptions import UserError


class BbbbeeGenerateEvidencePackWizard(models.TransientModel):
    _name = "bbbbee.generate.evidence.pack.wizard"
    _description = "Generate B-BBEE Evidence Pack"

    measurement_period_id = fields.Many2one("bbbbee.measurement.period", required=True)
    assessment_id = fields.Many2one("bbbbee.scorecard.assessment")

    def action_generate(self):
        assessment = self.assessment_id
        if not assessment and self.measurement_period_id.active_rule_set_id:
            assessment = self.env["bbbbee.scorecard.assessment"].search(
                [("measurement_period_id", "=", self.measurement_period_id.id)],
                limit=1,
            )
            if not assessment:
                assessment = self.env["bbbbee.scorecard.assessment"].create(
                    {
                        "name": "Assessment - %s" % self.measurement_period_id.name,
                        "measurement_period_id": self.measurement_period_id.id,
                        "rule_set_id": self.measurement_period_id.active_rule_set_id.id,
                        "spend_batch_ids": [
                            (
                                6,
                                0,
                                self.env["bbbbee.spend.batch"].search(
                                    [("measurement_period_id", "=", self.measurement_period_id.id)]
                                ).ids,
                            )
                        ],
                    }
                )
        if assessment and assessment.measurement_period_id != self.measurement_period_id:
            raise UserError("Selected assessment must belong to the selected measurement period.")
        pack = self.env["bbbbee.evidence.pack"].create(
            {
                "name": "Evidence Pack - %s" % self.measurement_period_id.name,
                "measurement_period_id": self.measurement_period_id.id,
                "assessment_id": assessment.id if assessment else False,
                "state": "generated",
            }
        )
        batches = self.env["bbbbee.spend.batch"].search([("measurement_period_id", "=", self.measurement_period_id.id)])
        supplier_ids = batches.mapped("line_ids.partner_id").ids
        missing_lines = self.env["bbbbee.evidence.completeness.checker"].find_missing_evidence(self.measurement_period_id)
        active_certificates = self.env["bbbbee.supplier.certificate"].search(
            [("state", "in", ("valid", "expiring_soon")), ("partner_id", "in", supplier_ids)]
        )
        self.env["bbbbee.evidence.item"].create(
            {
                "pack_id": pack.id,
                "name": "Summary for %s" % self.measurement_period_id.name,
                "item_type": "summary",
                "note": "Spend batches: %s. Missing evidence lines: %s."
                % (len(batches), len(missing_lines)),
            }
        )
        if batches:
            self.env["bbbbee.evidence.item"].create(
                {
                    "pack_id": pack.id,
                    "name": "Spend schedule",
                    "item_type": "spend_schedule",
                    "note": "Open the spend schedule report for the imported batch records in this period.",
                }
            )
        for line in missing_lines:
            self.env["bbbbee.evidence.item"].create(
                {
                    "pack_id": pack.id,
                    "name": "Missing evidence - %s" % line.partner_id.display_name,
                    "item_type": "missing_evidence",
                    "note": "Spend line %s requires review." % (line.display_name or line.id),
                }
            )
        for certificate in active_certificates:
            self.env["bbbbee.evidence.item"].create(
                {
                    "pack_id": pack.id,
                    "name": "Supplier certificate - %s" % certificate.partner_id.display_name,
                    "item_type": "certificate",
                    "attachment_id": certificate.attachment_id.id,
                    "note": "Evidence status: %s." % certificate.state,
                }
            )
        return {
            "type": "ir.actions.act_window",
            "res_model": "bbbbee.evidence.pack",
            "res_id": pack.id,
            "view_mode": "form",
            "target": "current",
        }
