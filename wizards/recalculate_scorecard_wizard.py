from odoo import fields, models


class BbbbeeRecalculateScorecardWizard(models.TransientModel):
    _name = "bbbbee.recalculate.scorecard.wizard"
    _description = "Recalculate B-BBEE Scorecard"

    assessment_id = fields.Many2one("bbbbee.scorecard.assessment", required=True)

    def action_recalculate(self):
        self.assessment_id.action_recalculate()
        return {
            "type": "ir.actions.act_window",
            "res_model": "bbbbee.scorecard.assessment",
            "res_id": self.assessment_id.id,
            "view_mode": "form",
        }
