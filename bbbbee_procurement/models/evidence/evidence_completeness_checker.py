from odoo import models


class BbbbeeEvidenceCompletenessChecker(models.AbstractModel):
    _name = "bbbbee.evidence.completeness.checker"
    _description = "Evidence Completeness Checker"

    def find_missing_evidence(self, measurement_period):
        return self.env["bbbbee.spend.line"].search(
            [
                ("batch_id.measurement_period_id", "=", measurement_period.id),
                ("evidence_status", "!=", "valid"),
            ]
        )
