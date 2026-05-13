from odoo import fields, models


class BbbbeeGenerateEvidencePackWizard(models.TransientModel):
    _name = "bbbbee.generate.evidence.pack.wizard"
    _description = "Generate B-BBEE Evidence Pack"

    measurement_period_id = fields.Many2one("bbbbee.measurement.period", required=True)
    assessment_id = fields.Many2one("bbbbee.scorecard.assessment")

    def action_generate(self):
        pack = self.env["bbbbee.evidence.pack"].create(
            {
                "name": "Evidence Pack - %s" % self.measurement_period_id.name,
                "measurement_period_id": self.measurement_period_id.id,
                "assessment_id": self.assessment_id.id,
                "state": "generated",
            }
        )
        return {
            "type": "ir.actions.act_window",
            "res_model": "bbbbee.evidence.pack",
            "res_id": pack.id,
            "view_mode": "form",
        }
