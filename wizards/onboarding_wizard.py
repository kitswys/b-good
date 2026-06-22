from odoo import fields, models


class BbbbeeOnboardingWizard(models.TransientModel):
    _name = "bbbbee.onboarding.wizard"
    _description = "B-BBEE Procurement Onboarding"

    overview_html = fields.Html(readonly=True)

    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        res["overview_html"] = """
            <div class="bbbbee-onboarding-hero">
                <div class="bbbbee-onboarding-kicker">Start Here</div>
                <h2>B-good launch path</h2>
                <p>Use this guided route to move from setup to a live scorecard with far less guesswork.</p>
                <div class="bbbbee-onboarding-stats">
                    <div><strong>4</strong><span>Setup steps</span></div>
                    <div><strong>1</strong><span>Single control center</span></div>
                    <div><strong>Live</strong><span>Risk visibility</span></div>
                </div>
                <div class="bbbbee-onboarding-summary">
                    <div><strong>Set framework</strong><span>Create periods and scoring rules.</span></div>
                    <div><strong>Load suppliers</strong><span>Attach profiles, certificates, and affidavits.</span></div>
                    <div><strong>Import spend</strong><span>Bring in posted spend and see exposure.</span></div>
                    <div><strong>Review results</strong><span>Recalculate, package, and share the outcome.</span></div>
                </div>
            </div>
            <div class="bbbbee-overview">
                <div class="bbbbee-overview-card">
                    <h3>What you get</h3>
                    <p>One control center for spend, supplier evidence, and score movement.</p>
                </div>
                <div class="bbbbee-overview-card">
                    <h3>First move</h3>
                    <p>Set measurement periods, then load suppliers and certificates.</p>
                </div>
                <div class="bbbbee-overview-card">
                    <h3>Result</h3>
                    <p>Clearer audit readiness, safer spend, and fewer verification surprises.</p>
                </div>
            </div>
        """
        return res

    def _open_action(self, xmlid):
        action = self.env.ref(xmlid).sudo().read()[0]
        action["target"] = "current"
        return action

    def action_open_supplier_profiles(self):
        return self._open_action("bbbbee_procurement.action_bbbbee_supplier_profile")

    def action_open_certificates(self):
        return self._open_action("bbbbee_procurement.action_bbbbee_supplier_certificate")

    def action_open_measurement_periods(self):
        return self._open_action("bbbbee_procurement.action_bbbbee_measurement_period")

    def action_open_rule_sets(self):
        return self._open_action("bbbbee_procurement.action_bbbbee_scorecard_rule_set")

    def action_open_spend_batches(self):
        return self._open_action("bbbbee_procurement.action_bbbbee_spend_batch")

    def action_open_assessments(self):
        return self._open_action("bbbbee_procurement.action_bbbbee_scorecard_assessment")

    def action_open_evidence_packs(self):
        return self._open_action("bbbbee_procurement.action_bbbbee_evidence_pack")

    def action_open_import_spend(self):
        action = self._open_action("bbbbee_procurement.action_bbbbee_import_spend_wizard")
        action["context"] = {
            "default_company_id": self.env.company.id,
        }
        return action

    def action_open_generate_evidence(self):
        action = self._open_action("bbbbee_procurement.action_bbbbee_generate_evidence_pack_wizard")
        action["context"] = {
            "default_company_id": self.env.company.id,
        }
        return action

    def action_open_recalculate_scorecard(self):
        return self._open_action("bbbbee_procurement.action_bbbbee_recalculate_scorecard_wizard")
