from odoo import models


class BbbbeeScorecardCalculator(models.AbstractModel):
    _name = "bbbbee.scorecard.calculator"
    _description = "B-BBEE Scorecard Calculator"

    def calculate_assessment(self, assessment):
        assessment.action_recalculate()
        return assessment
