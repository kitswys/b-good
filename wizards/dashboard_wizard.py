import base64
import math
from datetime import timedelta
from html import escape as html_escape

from odoo import api, fields, models
from odoo.exceptions import UserError


class BbbbeeDashboardWizard(models.TransientModel):
    _name = "bbbbee.dashboard.wizard"
    _description = "B-BBEE Procurement Dashboard"

    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.company,
        required=True,
        help="Company the dashboard is showing.",
    )
    measurement_period_id = fields.Many2one(
        "bbbbee.measurement.period",
        help="Date range the dashboard should measure.",
    )
    expiry_window_days = fields.Selection(
        [
            ("7", "7 days"),
            ("14", "14 days"),
            ("30", "30 days"),
            ("60", "60 days"),
            ("90", "90 days"),
        ],
        default="30",
        help="How many days ahead to show certificates and affidavits that are about to expire.",
    )
    has_data = fields.Boolean(compute="_compute_dashboard")
    supplier_profile_count = fields.Integer(compute="_compute_dashboard")
    supplier_certificate_count = fields.Integer(compute="_compute_dashboard")
    valid_certificate_count = fields.Integer(compute="_compute_dashboard")
    expiring_certificate_count = fields.Integer(compute="_compute_dashboard")
    missing_evidence_count = fields.Integer(compute="_compute_dashboard")
    missing_certificate_count = fields.Integer(compute="_compute_dashboard")
    spend_batch_count = fields.Integer(compute="_compute_dashboard")
    spend_line_count = fields.Integer(compute="_compute_dashboard")
    high_risk_supplier_count = fields.Integer(compute="_compute_dashboard")
    total_measured_spend = fields.Monetary(compute="_compute_dashboard")
    recognised_procurement_spend = fields.Monetary(compute="_compute_dashboard")
    target_percentage = fields.Float(compute="_compute_dashboard")
    achieved_percentage = fields.Float(compute="_compute_dashboard")
    shortfall_amount = fields.Monetary(compute="_compute_dashboard")
    compliance_rate = fields.Float(compute="_compute_dashboard")
    evidence_gap_rate = fields.Float(compute="_compute_dashboard")
    recognised_severity = fields.Selection(
        [("good", "Good"), ("warn", "Warning"), ("risk", "Risk")],
        compute="_compute_dashboard",
    )
    missing_severity = fields.Selection(
        [("good", "Good"), ("warn", "Warning"), ("risk", "Risk")],
        compute="_compute_dashboard",
    )
    high_risk_severity = fields.Selection(
        [("good", "Good"), ("warn", "Warning"), ("risk", "Risk")],
        compute="_compute_dashboard",
    )
    currency_id = fields.Many2one(related="company_id.currency_id")
    ownership_score = fields.Float(compute="_compute_dashboard")
    management_control_score = fields.Float(compute="_compute_dashboard")
    skills_development_score = fields.Float(compute="_compute_dashboard")
    esd_score = fields.Float(compute="_compute_dashboard")
    sed_score = fields.Float(compute="_compute_dashboard")
    overall_score = fields.Float(compute="_compute_dashboard")
    bee_level_score = fields.Float(compute="_compute_dashboard")
    bee_level = fields.Char(compute="_compute_dashboard")
    bee_status = fields.Selection(
        [("good", "Good"), ("okay", "Okay"), ("risk", "At Risk")],
        compute="_compute_dashboard",
    )
    bee_status_label = fields.Char(compute="_compute_dashboard")
    bee_status_note = fields.Char(compute="_compute_dashboard")
    scorecard_html = fields.Html(compute="_compute_dashboard", sanitize=False)
    business_impact_html = fields.Html(compute="_compute_dashboard", sanitize=False)
    fastest_path_html = fields.Html(compute="_compute_dashboard", sanitize=False)
    forecast_html = fields.Html(compute="_compute_dashboard", sanitize=False)
    blocking_html = fields.Html(compute="_compute_dashboard", sanitize=False)
    overview_html = fields.Html(compute="_compute_dashboard", sanitize=False)
    visual_html = fields.Html(compute="_compute_dashboard", sanitize=False)
    help_html = fields.Html(compute="_compute_dashboard", sanitize=False)
    info_html = fields.Html(compute="_compute_dashboard", sanitize=False)
    expiring_documents_html = fields.Html(compute="_compute_dashboard", sanitize=False)
    starter_html = fields.Html(compute="_compute_dashboard", sanitize=False)
    next_actions_html = fields.Html(compute="_compute_dashboard", sanitize=False)
    info_key = fields.Char()

    def _default_measurement_period(self):
        period = self.env["bbbbee.measurement.period"].search(
            [("company_id", "=", self.env.company.id)],
            order="date_end desc, id desc",
            limit=1,
        )
        return period

    def _ensure_demo_attachment(self, name="B-good Starter Certificate.txt"):
        attachment = self.env["ir.attachment"].search(
            [("name", "=", name), ("res_model", "=", "bbbbee.supplier.certificate")],
            limit=1,
        )
        if not attachment:
            attachment = self.env["ir.attachment"].create(
                {
                    "name": name,
                    "type": "binary",
                    "datas": base64.b64encode(b"Sample B-BBEE evidence for first-time walkthrough."),
                    "mimetype": "text/plain",
                    "res_model": "bbbbee.supplier.certificate",
                }
            )
        return attachment

    def _starter_period_label(self):
        year = fields.Date.context_today(self).year
        return "Starter FY%s" % year

    def _get_or_create_rule_set(self):
        rule_set = self.env["bbbbee.scorecard.rule.set"].search(
            [("company_id", "=", self.company_id.id), ("state", "=", "active")],
            order="effective_date desc, id desc",
            limit=1,
        )
        if not rule_set:
            rule_set = self.env["bbbbee.scorecard.rule.set"].create(
                {
                    "name": "Starter Rule Set - %s" % self.company_id.name,
                    "company_id": self.company_id.id,
                    "effective_date": fields.Date.context_today(self),
                    "target_percentage": 80.0,
                    "available_points": 25.0,
                    "state": "active",
                }
            )
        return rule_set

    def _build_plain_language_help(self, has_data, expiring_count, missing_count):
        if not has_data:
            return """
                <div style="border:1px solid #d6e0f5;border-radius:12px;padding:16px 18px;background:linear-gradient(135deg,#ffffff 0%%,#f7faff 100%%);margin-bottom:12px;">
                    <div style="font-size:11px;font-weight:800;letter-spacing:0.03em;text-transform:uppercase;color:#2f5be3;margin-bottom:6px;">Getting Started</div>
                    <div style="font-size:18px;font-weight:800;color:#1f2d3d;margin-bottom:6px;">This dashboard is your setup screen</div>
                    <div style="font-size:13px;color:#52627c;line-height:1.6;margin-bottom:12px;">
                        When there is no data yet, use this page to understand the module and load a starter workflow.
                        <strong>Measurement period</strong> means the date range you want to measure.
                        <strong>Recognised spend</strong> is the portion of spend that counts.
                        <strong>Audit pack</strong> is the bundle you share for review.
                    </div>
                    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:10px;">
                        <div style="padding:12px;border:1px solid #e5e7eb;border-radius:10px;background:#fff;">
                            <div style="font-size:11px;font-weight:800;color:#2f5be3;margin-bottom:4px;">1. Create your period</div>
                            <div style="font-size:13px;color:#52627c;">Set the date range the scorecard should measure.</div>
                        </div>
                        <div style="padding:12px;border:1px solid #e5e7eb;border-radius:10px;background:#fff;">
                            <div style="font-size:11px;font-weight:800;color:#2f5be3;margin-bottom:4px;">2. Load a sample workflow</div>
                            <div style="font-size:13px;color:#52627c;">Use starter data to see how the module behaves immediately.</div>
                        </div>
                        <div style="padding:12px;border:1px solid #e5e7eb;border-radius:10px;background:#fff;">
                            <div style="font-size:11px;font-weight:800;color:#2f5be3;margin-bottom:4px;">3. Add real suppliers</div>
                            <div style="font-size:13px;color:#52627c;">Build supplier profiles and upload certificates or affidavits.</div>
                        </div>
                        <div style="padding:12px;border:1px solid #e5e7eb;border-radius:10px;background:#fff;">
                            <div style="font-size:11px;font-weight:800;color:#2f5be3;margin-bottom:4px;">4. Import spend</div>
                            <div style="font-size:13px;color:#52627c;">Bring in posted bills and see what is at risk or ready.</div>
                        </div>
                    </div>
                </div>
            """
        return """
            <div style="border:1px solid #d6e0f5;border-radius:12px;padding:14px 16px;background:#fff;margin-bottom:12px;">
                <div style="font-size:11px;font-weight:800;letter-spacing:0.03em;text-transform:uppercase;color:#2f5be3;margin-bottom:6px;">Next Steps</div>
                <div style="font-size:13px;color:#52627c;line-height:1.6;margin-bottom:10px;">
                    %s certificates are expiring within your selected window. %s spend lines still need review.
                    Start by fixing the supplier records that matter most, then recalculate the scorecard.
                </div>
                <div style="display:flex;flex-wrap:wrap;gap:8px;">
                    <span style="padding:6px 10px;border-radius:999px;background:#f3f6fb;color:#1f2d3d;font-size:12px;font-weight:700;">Measurement period = the date range you are measuring</span>
                    <span style="padding:6px 10px;border-radius:999px;background:#f3f6fb;color:#1f2d3d;font-size:12px;font-weight:700;">Recognised spend = the spend that counts</span>
                    <span style="padding:6px 10px;border-radius:999px;background:#f3f6fb;color:#1f2d3d;font-size:12px;font-weight:700;">Audit pack = the bundle you export for review</span>
                </div>
            </div>
        """ % (expiring_count, missing_count)

    def _bee_level_for_score(self, score):
        bands = [
            (90.0, "Level 1"),
            (80.0, "Level 2"),
            (70.0, "Level 3"),
            (60.0, "Level 4"),
            (50.0, "Level 5"),
            (40.0, "Level 6"),
            (30.0, "Level 7"),
            (0.0, "Level 8"),
        ]
        for threshold, label in bands:
            if score >= threshold:
                return label
        return "Level 8"

    def _next_level_gap(self, score):
        thresholds = [90.0, 80.0, 70.0, 60.0, 50.0, 40.0, 30.0]
        for threshold in thresholds:
            if score < threshold:
                gap = threshold - score
                return threshold, int(math.ceil(gap)), "point" if int(math.ceil(gap)) == 1 else "points"
        return None, 0, "points"

    def _next_level_transition(self, score):
        current_level = self._bee_level_for_score(score)
        if not current_level.startswith("Level "):
            return current_level, None, 0, "points"
        current_level_num = int(current_level.split()[-1])
        if current_level_num <= 1:
            return current_level, None, 0, "points"
        next_level_num = current_level_num - 1
        next_level_label = "Level %s" % next_level_num
        level_thresholds = {
            1: 90.0,
            2: 80.0,
            3: 70.0,
            4: 60.0,
            5: 50.0,
            6: 40.0,
            7: 30.0,
        }
        next_threshold = level_thresholds.get(next_level_num, 0.0)
        gap = max(0.0, next_threshold - score)
        points = int(math.ceil(gap))
        return current_level, next_level_label, points, "point" if points == 1 else "points"

    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        period = self._default_measurement_period()
        if period:
            res["measurement_period_id"] = period.id
        info_key = self.env.context.get("default_info_key") or self.env.context.get("dashboard_info_key")
        if info_key:
            res["info_key"] = info_key
        return res

    @api.depends("company_id", "measurement_period_id", "info_key", "expiry_window_days")
    def _compute_dashboard(self):
        for dashboard in self:
            period = dashboard.measurement_period_id or dashboard._default_measurement_period()
            period_domain = [("measurement_period_id", "=", period.id)] if period else [("id", "=", 0)]
            batches = self.env["bbbbee.spend.batch"].search(period_domain)
            lines = (
                self.env["bbbbee.spend.line"].search([("batch_id", "in", batches.ids)])
                if batches
                else self.env["bbbbee.spend.line"].browse()
            )
            assessments = (
                self.env["bbbbee.scorecard.assessment"].search(period_domain)
                if period
                else self.env["bbbbee.scorecard.assessment"].browse()
            )
            assessment = assessments[:1]
            supplier_profiles = self.env["bbbbee.supplier.profile"].search([])
            certificates = self.env["bbbbee.supplier.certificate"].search([])
            valid_certificates = certificates.filtered(lambda certificate: certificate.state == "valid")
            expiring_certificates = certificates.filtered(lambda certificate: certificate.state == "expiring_soon")
            missing_lines = lines.filtered(lambda line: line.evidence_status in ("missing", "review_required"))
            risk_service = self.env["bbbbee.supplier.risk.service"]
            high_risk_supplier_count = sum(
                1 for profile in supplier_profiles if risk_service.get_risk_level(profile.partner_id) == "high"
            )

            dashboard.supplier_profile_count = len(supplier_profiles)
            dashboard.supplier_certificate_count = len(certificates)
            dashboard.valid_certificate_count = len(valid_certificates)
            dashboard.expiring_certificate_count = len(expiring_certificates)
            dashboard.missing_certificate_count = len(certificates.filtered(lambda c: c.state == "missing"))
            dashboard.missing_evidence_count = len(missing_lines)
            dashboard.spend_batch_count = len(batches)
            dashboard.spend_line_count = len(lines)
            dashboard.high_risk_supplier_count = high_risk_supplier_count
            dashboard.has_data = bool(supplier_profiles or certificates or batches or assessments)
            dashboard.compliance_rate = (
                (len(valid_certificates) / len(certificates) * 100.0) if certificates else 0.0
            )
            dashboard.evidence_gap_rate = (
                (len(missing_lines) / len(lines) * 100.0) if lines else 0.0
            )
            ownership_values = supplier_profiles.mapped("black_ownership_percentage")
            ownership_values = [value for value in ownership_values if value is not None]
            ownership_score = sum(ownership_values) / len(ownership_values) if ownership_values else 0.0
            management_score = (
                (len(supplier_profiles.filtered(lambda p: p.empowering_supplier_status == "yes")) / len(supplier_profiles) * 100.0)
                if supplier_profiles
                else 0.0
            )
            skills_score = (
                (len(certificates.filtered(lambda c: c.attachment_id)) / len(certificates) * 100.0)
                if certificates
                else 0.0
            )
            esd_score = 0.0
            sed_score = max(0.0, 100.0 - dashboard.evidence_gap_rate)
            dashboard.ownership_score = max(0.0, min(100.0, ownership_score))
            dashboard.management_control_score = max(0.0, min(100.0, management_score))
            dashboard.skills_development_score = max(0.0, min(100.0, skills_score))
            dashboard.sed_score = max(0.0, min(100.0, sed_score))
            dashboard.overall_score = (
                dashboard.ownership_score
                + dashboard.management_control_score
                + dashboard.skills_development_score
                + dashboard.esd_score
                + dashboard.sed_score
            ) / 5.0

            if dashboard.evidence_gap_rate > 25.0:
                dashboard.missing_severity = "risk"
            elif dashboard.evidence_gap_rate > 10.0:
                dashboard.missing_severity = "warn"
            else:
                dashboard.missing_severity = "good"
            if high_risk_supplier_count >= 5:
                dashboard.high_risk_severity = "risk"
            elif high_risk_supplier_count > 0:
                dashboard.high_risk_severity = "warn"
            else:
                dashboard.high_risk_severity = "good"

            if dashboard.has_data:
                dashboard.starter_html = ""
                dashboard.next_actions_html = ""
            else:
                dashboard.starter_html = self._build_plain_language_help(False, 0, 0)
                dashboard.next_actions_html = ""

            if assessment:
                dashboard.total_measured_spend = assessment.total_measured_spend
                dashboard.recognised_procurement_spend = assessment.recognised_procurement_spend
                dashboard.target_percentage = assessment.target_percentage
                dashboard.achieved_percentage = assessment.achieved_percentage
                dashboard.shortfall_amount = assessment.shortfall_amount
            else:
                dashboard.total_measured_spend = 0.0
                dashboard.recognised_procurement_spend = 0.0
                dashboard.target_percentage = 80.0
                dashboard.achieved_percentage = 0.0
                dashboard.shortfall_amount = 0.0
            esd_score = (
                (dashboard.recognised_procurement_spend / dashboard.total_measured_spend * 100.0)
                if dashboard.total_measured_spend
                else 0.0
            )
            dashboard.esd_score = max(0.0, min(100.0, esd_score))
            if dashboard.achieved_percentage >= dashboard.target_percentage:
                dashboard.recognised_severity = "good"
            elif dashboard.achieved_percentage >= max(dashboard.target_percentage - 10.0, 0.0):
                dashboard.recognised_severity = "warn"
            else:
                dashboard.recognised_severity = "risk"

            bee_components = [
                dashboard.ownership_score,
                dashboard.management_control_score,
                dashboard.skills_development_score,
                dashboard.esd_score,
                dashboard.sed_score,
                dashboard.achieved_percentage,
                dashboard.compliance_rate,
                max(0.0, 100.0 - dashboard.evidence_gap_rate),
                max(0.0, 100.0 - min(100.0, high_risk_supplier_count * 10.0)),
            ]
            dashboard.bee_level_score = sum(bee_components) / len(bee_components) if bee_components else 0.0
            dashboard.bee_level = self._bee_level_for_score(dashboard.bee_level_score)

            if dashboard.bee_level_score >= 75.0 and dashboard.evidence_gap_rate <= 10.0 and dashboard.achieved_percentage >= dashboard.target_percentage:
                dashboard.bee_status = "good"
                dashboard.bee_status_label = "You are in the green"
                dashboard.bee_status_note = "Good shape: lower compliance risk and better access to benefits."
            elif dashboard.bee_level_score >= 55.0:
                dashboard.bee_status = "okay"
                dashboard.bee_status_label = "You are in the amber"
                dashboard.bee_status_note = "Okay, but keep closing gaps to protect benefits and avoid fees."
            else:
                dashboard.bee_status = "risk"
                dashboard.bee_status_label = "You are in the red"
                dashboard.bee_status_note = "At risk: higher chance of penalties, fees, or reduced benefits."

            period_name = period.name if period else "No measurement period selected"
            achieved_pct = max(0.0, min(100.0, dashboard.achieved_percentage))
            compliance_pct = max(0.0, min(100.0, dashboard.compliance_rate))
            gap_pct = max(0.0, min(100.0, dashboard.evidence_gap_rate))
            achieved_class = "good" if dashboard.achieved_percentage >= dashboard.target_percentage else "warn"
            compliance_class = "good" if dashboard.compliance_rate >= 80.0 else "warn"
            gap_class = "good" if dashboard.evidence_gap_rate <= 10.0 else "risk"
            dashboard.overview_html = ""
            classification_totals = {
                "included": sum(lines.filtered(lambda line: line.classification == "included").mapped("included_amount")),
                "review": sum(lines.filtered(lambda line: line.classification == "review").mapped("included_amount")),
                "excluded": sum(lines.filtered(lambda line: line.classification == "excluded").mapped("included_amount")),
            }
            evidence_totals = {
                "valid": sum(lines.filtered(lambda line: line.evidence_status == "valid").mapped("included_amount")),
                "review_required": sum(lines.filtered(lambda line: line.evidence_status == "review_required").mapped("included_amount")),
                "missing": sum(lines.filtered(lambda line: line.evidence_status == "missing").mapped("included_amount")),
                "expired": sum(lines.filtered(lambda line: line.evidence_status == "expired").mapped("included_amount")),
            }
            certificate_totals = {
                "valid": len(valid_certificates),
                "expiring_soon": len(expiring_certificates),
                "missing": len(certificates.filtered(lambda c: c.state == "missing")),
                "expired": len(certificates.filtered(lambda c: c.state == "expired")),
            }
            assessment_history = self.env["bbbbee.scorecard.assessment"].search(
                [("company_id", "=", dashboard.company_id.id)]
            )
            assessment_history = sorted(
                assessment_history,
                key=lambda rec: (rec.measurement_period_id.date_end or fields.Date.to_date("1970-01-01"), rec.id),
            )
            today = fields.Date.context_today(dashboard)
            window_days = max(int(dashboard.expiry_window_days or 30), 1)
            upcoming_expiries = sorted(
                certificates.filtered(
                    lambda c: c.active
                    and c.expiry_date
                    and 0 <= (c.expiry_date - today).days <= window_days
                ),
                key=lambda cert: cert.expiry_date,
            )
            next_expiries_html = []
            for cert in upcoming_expiries:
                days_remaining = (cert.expiry_date - today).days if cert.expiry_date else 0
                next_expiries_html.append(
                    """
                    <div style="display:flex;justify-content:space-between;gap:10px;align-items:flex-start;padding:8px 10px;border-radius:8px;background:#f3f6fb;font-size:12px;color:#52627c;">
                        <span style="min-width:0;"><strong style="color:#1f2d3d;">%s</strong><br/>%s</span>
                        <strong style="color:#1f2d3d;white-space:nowrap;">%s days</strong>
                    </div>
                    """
                    % (
                        html_escape(cert.partner_id.display_name or "Unknown supplier"),
                        html_escape("%s (%s)" % (cert.expiry_date.strftime("%d %b %Y"), (cert.certificate_type or "certificate").replace("_", " "))),
                        days_remaining,
                    )
                )
            if not next_expiries_html:
                next_expiries_html.append(
                    """
                    <div style="padding:8px 10px;border-radius:8px;background:#f3f6fb;font-size:12px;color:#64748b;">
                        No certificates or affidavits are expiring in the next %s days.
                    </div>
                    """
                    % window_days
                )
            dashboard.expiring_documents_html = ""
            missing_spend_by_partner = {}
            for line in lines.filtered(lambda line: line.evidence_status == "missing" and line.partner_id):
                partner_data = missing_spend_by_partner.setdefault(
                    line.partner_id.id,
                    {"name": line.partner_id.display_name or "Unknown supplier", "spend": 0.0},
                )
                partner_data["spend"] += line.included_amount or 0.0
            top_missing_partner = max(missing_spend_by_partner.values(), key=lambda item: item["spend"]) if missing_spend_by_partner else None
            latest_movement = 0.0
            latest_movement_period = period_name
            if len(assessment_history) >= 2:
                latest = assessment_history[-1]
                previous = assessment_history[-2]
                latest_movement = (latest.achieved_percentage or 0.0) - (previous.achieved_percentage or 0.0)
                latest_movement_period = latest.measurement_period_id.name or period_name
            elif assessment_history:
                latest = assessment_history[-1]
                latest_movement = latest.achieved_percentage or 0.0
                latest_movement_period = latest.measurement_period_id.name or period_name
            score_bars = [
                ("Ownership", dashboard.ownership_score, "Capture real ownership percentages and keep evidence current."),
                (
                    "Management Control",
                    dashboard.management_control_score,
                    "Improve representation in leadership and maintain supporting governance records.",
                ),
                (
                    "Skills Development",
                    dashboard.skills_development_score,
                    "Upload training evidence, learnership records, and bursary/skills documentation.",
                ),
                (
                    "Enterprise & Supplier Development",
                    dashboard.esd_score,
                    "Shift spend to compliant suppliers and increase support for black-owned SMEs.",
                ),
                (
                    "Socio-Economic Development",
                    dashboard.sed_score,
                    "Close evidence gaps and record qualifying development contributions.",
                ),
            ]
            score_rows = []
            for label, value, tip in score_bars:
                if value >= 75.0:
                    bar_color = "linear-gradient(90deg,#16a34a,#4ade80)"
                elif value >= 45.0:
                    bar_color = "linear-gradient(90deg,#f59e0b,#fbbf24)"
                else:
                    bar_color = "linear-gradient(90deg,#ef4444,#f87171)"
                score_rows.append(
                    """
                    <div style="border:1px solid #dbe2ee;border-radius:8px;padding:10px 12px;background:#fff;">
                        <div style="display:flex;justify-content:space-between;gap:12px;font-size:13px;">
                            <strong>%s</strong><strong>%0.1f%%</strong>
                        </div>
                        <div style="height:10px;background:#edf1f6;border-radius:999px;overflow:hidden;margin:8px 0 6px;">
                            <div style="height:100%%;width:%0.1f%%;background:%s;"></div>
                        </div>
                        <div style="font-size:12px;color:#52627c;">How to improve: %s</div>
                    </div>
                    """ % (label, value, value, bar_color, tip)
                )
            _, next_level_label, points_to_next_level, points_label = self._next_level_transition(
                dashboard.bee_level_score
            )
            risk_level = "HIGH" if dashboard.bee_status == "risk" else "LOW"
            evidence_improvement = max(0.0, round(min(6.0, dashboard.evidence_gap_rate / 10.0), 0))
            supplier_improvement = max(0.0, round(min(4.0, dashboard.high_risk_supplier_count * 0.8), 0))
            missing_evidence_spend = sum(missing_lines.mapped("included_amount")) if missing_lines else 0.0
            verification_gap_spend = max(0.0, dashboard.total_measured_spend - dashboard.recognised_procurement_spend)
            high_risk_partner_ids = [
                profile.partner_id.id
                for profile in supplier_profiles
                if risk_service.get_risk_level(profile.partner_id) == "high"
            ]
            high_risk_lines = lines.filtered(lambda line: line.partner_id.id in high_risk_partner_ids)
            high_risk_spend = sum(high_risk_lines.mapped("included_amount")) if high_risk_lines else 0.0
            currency = self.env.company.currency_id

            def _money(amount):
                return "%s %s" % ((currency.symbol or "R"), format(amount or 0.0, ",.2f"))

            compliance_reason = (
                "Critical operational risk levels based on missing compliance items and exposure metrics."
            )
            missing_reason = (
                "%s spend lines still need verification. This can exclude spend from recognised value."
                % dashboard.missing_evidence_count
            )
            supplier_reason = (
                "%s suppliers are flagged high risk by ownership or compliance signals."
                % dashboard.high_risk_supplier_count
            )
            evidence_path_reason = "Actionable strategic checklist steps to unlock your next target compliance level."
            supplier_mix_reason = "Reduce supplier risk to improve recognised value and audit confidence."
            level_reason = "Current score of %0.1f%% maps to %s." % (dashboard.bee_level_score, dashboard.bee_level)
            score_reason = "Higher score improves compliance position and audit readiness."
            readiness_reason = dashboard.bee_status_note
            bee_level_reason = "This is your current B-BBEE level. Lower level numbers are stronger."
            snapshot_reason = "Your officially recognized B-BBEE level based on your verified scorecard calculations."
            in_scope_reason = "Total financial spend extracted from posted vendor bills within this active evaluation period."
            verified_reason = "The safe portion of your procurement spend backed by valid, certified compliance documentation."
            current_score_reason = "Your current calculated procurement point progress matched directly against your corporate target threshold."
            supplier_health_reason = "The percentage of active vendors in your supply chain with up-to-date, valid B-BBEE certificates."
            spend_at_risk_reason = "Rand value vulnerable to auditor rejection due to missing or expired supplier paperwork."
            info_key = dashboard.info_key or self.env.context.get("dashboard_info_key") or self.env.context.get("default_info_key")

            def _info_icon(text, key):
                safe_text = html_escape(text)
                return (
                    f'<i class="fa fa-info-circle text-muted ml-1 bbbbee-info-trigger" '
                    f'data-info-key="{html_escape(key)}" title="{safe_text}" style="cursor:help;"></i>'
                )

            business_impact_icon = _info_icon(compliance_reason, "business_impact")
            fastest_path_icon = _info_icon(evidence_path_reason, "fastest_improvement_path")

            def _info_page_html(key):
                pages = {
                    "executive_snapshot": {
                        "title": "Executive Snapshot",
                        "lede": snapshot_reason,
                        "sections": [
                            ("What it means", "This is the highest-level summary of your current B-BBEE position for the selected period."),
                            ("What drives it", "It reflects recognised spend, evidence quality, supplier compliance, and risk exposure."),
                            ("How levels work", "B-BBEE levels run from Level 1 to Level 8. Level 1 is the strongest position and Level 8 is the weakest. A lower level number means a stronger compliance position, better procurement recognition, and less risk in external review."),
                            ("Level guide", "Level 1: strongest compliance result. Level 2: very strong. Level 3: strong. Level 4: acceptable. Level 5: moderate. Level 6: weak. Level 7: high risk. Level 8: weakest result."),
                            ("What to do next", "Use the score gap and risk indicators to prioritise the next strongest improvement action."),
                        ],
                    },
                    "business_impact": {
                        "title": "Business Impact",
                        "lede": compliance_reason,
                        "sections": [
                            ("Why it matters", "This shows the operational consequences of missing evidence and high exposure."),
                            ("What changes the status", "Compliance risk improves when verification gaps shrink and supplier evidence is current."),
                            ("What to do next", "Review the highest-risk items first because they affect the score and verification outcome fastest."),
                        ],
                    },
                    "fastest_improvement_path": {
                        "title": "Fastest Improvement Path",
                        "lede": evidence_path_reason,
                        "sections": [
                            ("Why this matters", "These are the shortest actions that recover score and reduce compliance exposure fastest."),
                            ("How to use it", "Work from the top item downward until the verification gap closes and supplier risk reduces."),
                            ("What happens when fixed", "Improvement here raises recognised spend and reduces the chance of audit rejection."),
                        ],
                    },
                    "in_scope_spend": {
                        "title": "In-Scope Spend",
                        "lede": in_scope_reason,
                        "sections": [
                            ("What it means", "This is the total spend imported from posted vendor bills for the active evaluation period."),
                            ("Why it matters", "It is the base number that the rest of the scorecard is judged against."),
                            ("How to improve it", "Keep spend records complete and tied to the right measurement period."),
                        ],
                    },
                    "verification_ready_spend": {
                        "title": "Verification-Ready Spend",
                        "lede": verified_reason,
                        "sections": [
                            ("What it means", "This is the spend that can safely count because the documents are valid and complete."),
                            ("Why it matters", "A higher value here increases recognised spend and strengthens the scorecard."),
                            ("How to improve it", "Upload missing supplier evidence and resolve expired or disputed records."),
                        ],
                    },
                    "current_period_score": {
                        "title": "Current Period Score",
                        "lede": current_score_reason,
                        "sections": [
                            ("What it means", "This bar shows how far the current period has progressed against the target framework."),
                            ("Why it matters", "It gives an at-a-glance view of whether the business is moving toward the required level."),
                            ("How to improve it", "Recover points by clearing verification gaps and improving the supplier mix."),
                        ],
                    },
                    "supplier_compliance_health": {
                        "title": "Supplier Compliance Health",
                        "lede": supplier_health_reason,
                        "sections": [
                            ("What it means", "This shows the share of vendors with valid, unexpired compliance documents."),
                            ("Why it matters", "Better supplier compliance means less spend is exposed to audit rejection."),
                            ("How to improve it", "Keep certificates current and replace weak suppliers where needed."),
                        ],
                    },
                    "spend_at_risk": {
                        "title": "Risk Exposure",
                        "lede": spend_at_risk_reason,
                        "sections": [
                            ("What it means", "This is the rand value that may fail review because supporting paperwork is missing or expired."),
                            ("Why it matters", "Higher exposure reduces the spend that can be recognised on the scorecard."),
                            ("How to improve it", "Fix missing evidence first, then recalculate the scorecard to confirm the recovered value."),
                        ],
                    },
                    "bee_level": {
                        "title": "B-BBEE Level",
                        "lede": bee_level_reason,
                        "sections": [
                            ("What it means", "Your B-BBEE level is the overall grade that tells the business how strong its procurement compliance position is."),
                            ("How the levels work", "There are eight levels. Level 1 is the strongest result and Level 8 is the weakest. The lower the number, the better the outcome."),
                            ("Why it matters", "The level affects how your business is viewed in procurement, audit review, and supplier compliance assessment."),
                            ("Level guide", "Level 1: strongest. Level 2: very strong. Level 3: strong. Level 4: acceptable. Level 5: moderate. Level 6: weak. Level 7: high risk. Level 8: weakest."),
                            ("What to do next", "Use the level together with the score, risk, and spend at risk indicators to decide which compliance gaps to fix first."),
                        ],
                    },
                }
                page = pages.get(key)
                if not page:
                    return "<div class='text-muted'>No detail is available for this item.</div>"
                body = [
                    "<div style='display:grid;gap:12px;'>",
                    "<div style='padding:14px 16px;border:1px solid #dbe2ee;border-radius:10px;background:#f8fafc;'>",
                    "<div style='font-size:11px;font-weight:800;letter-spacing:0.03em;text-transform:uppercase;color:#2f5be3;margin-bottom:6px;'>%s</div>" % html_escape(page["title"]),
                    "<div style='font-size:14px;color:#1f2d3d;line-height:1.6;'>%s</div>" % html_escape(page["lede"]),
                    "</div>",
                ]
                for heading, text in page["sections"]:
                    body.extend(
                        [
                            "<div style='padding:14px 16px;border:1px solid #e5e7eb;border-radius:10px;background:#fff;'>",
                            "<div style='font-size:13px;font-weight:800;color:#1f2d3d;margin-bottom:6px;'>%s</div>" % html_escape(heading),
                            "<div style='font-size:13px;color:#52627c;line-height:1.6;'>%s</div>" % html_escape(text),
                            "</div>",
                        ]
                    )
                body.append("</div>")
                return "".join(body)

            ring_html = """
                <div title="{score_reason}" style="width:160px;height:160px;border-radius:50%;background:conic-gradient(#2f5be3 0 {score:.1f}%, #d7deea {score:.1f}% 100%);flex:0 0 160px;position:relative;">
                    <div style="position:absolute;inset:16px;border-radius:50%;background:#fff;display:flex;align-items:center;justify-content:center;font-size:34px;font-weight:900;color:#1f2d3d;">{score:.0f}%</div>
                </div>
            """.format(score=dashboard.bee_level_score, score_reason=score_reason)
            hero_context_html = """
                <div class="p-3" style="margin-top:18px;border-radius:12px;background:#fff;border:1px solid #e3e9f4;">
                    <div style="font-size:11px;font-weight:800;letter-spacing:0.03em;text-transform:uppercase;color:#2f5be3;margin-bottom:8px;">At a Glance</div>
                    <div style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;">
                        <div>
                            <div style="font-size:11px;font-weight:700;color:#52627c;margin-bottom:4px;">Target Progress</div>
                            <div style="font-size:18px;font-weight:800;color:#1f2d3d;">{audit_readiness:.1f}%</div>
                            <div style="font-size:12px;color:#64748b;">Your current period progress toward the target threshold.</div>
                        </div>
                        <div>
                            <div style="font-size:11px;font-weight:700;color:#52627c;margin-bottom:4px;">Risk Exposure</div>
                            <div style="font-size:18px;font-weight:800;color:#1f2d3d;">{spend_at_risk}</div>
                            <div style="font-size:12px;color:#64748b;">Spend exposed to missing or expired evidence.</div>
                        </div>
                    </div>
                    <div style="margin-top:12px;padding:10px 12px;border-radius:10px;background:#f8fafc;border:1px solid #e5e7eb;">
                        <div style="font-size:11px;font-weight:700;color:#52627c;margin-bottom:4px;">Current Status</div>
                        <div style="font-size:18px;font-weight:900;color:#1f2d3d;">{bee_status_label}</div>
                        <div style="font-size:12px;color:#64748b;">{bee_status_note}</div>
                    </div>
                </div>
            """.format(
                audit_readiness=dashboard.achieved_percentage,
                spend_at_risk=_money(verification_gap_spend),
                bee_status_label=dashboard.bee_status_label,
                bee_status_note=dashboard.bee_status_note,
            )
            dashboard.scorecard_html = """
                <div style="border:1px solid #d6e0f5;border-radius:10px;padding:18px 18px 16px;background:linear-gradient(135deg,#f7faff 0%%,#eef4ff 100%%);min-height:170px;display:flex;justify-content:space-between;gap:18px;align-items:flex-start;">
                    <div style="min-width:0;">
                        <div style="font-size:11px;font-weight:800;letter-spacing:0.03em;text-transform:uppercase;color:#2f5be3;margin-bottom:8px;display:flex;align-items:center;gap:4px;">Executive Snapshot{executive_snapshot_icon}</div>
                        <div style="font-size:13px;color:#52627c;margin-bottom:10px;">{company_name} / {period_name}</div>
                        <div title="{level_reason}" style="font-size:32px;font-weight:900;line-height:1;color:#1f2d3d;margin-bottom:4px;display:flex;align-items:center;gap:4px;">{bee_level}{bee_level_icon}</div>
                        <div title="{score_reason}" style="font-size:84px;font-weight:900;line-height:0.86;color:#1f2d3d;">{bee_level_score_text}<span style="font-size:24px;font-weight:800;color:#64748b;">/100</span></div>
                        <div title="{readiness_reason}" style="font-size:14px;font-weight:700;color:#64748b;margin-top:10px;">{level_gap_text}</div>
                        {hero_context_html}
                    </div>
                    {ring_html}
                </div>
            """.format(
                company_name=dashboard.company_id.name,
                period_name=period_name,
                level_gap_text="Top level reached"
                if next_level_label is None
                else "%d %s to %s" % (points_to_next_level, points_label, next_level_label),
                risk_level=risk_level,
                missing_evidence_count=dashboard.missing_evidence_count,
                high_risk_supplier_count=dashboard.high_risk_supplier_count,
                evidence_improvement=evidence_improvement,
                supplier_improvement=supplier_improvement,
                bee_level_score_text="%0.0f" % dashboard.bee_level_score,
                bee_level=dashboard.bee_level,
                ring_html=ring_html,
                score_rows="".join(score_rows),
                compliance_reason=compliance_reason,
                missing_reason=missing_reason,
                supplier_reason=supplier_reason,
                evidence_path_reason=evidence_path_reason,
                supplier_mix_reason=supplier_mix_reason,
                level_reason=level_reason,
                score_reason=score_reason,
                readiness_reason=readiness_reason,
                bee_level_icon=_info_icon(bee_level_reason, "bee_level"),
                missing_certificate_impact="+%0.0f pts" % evidence_improvement,
                verification_gap_spend_text=_money(verification_gap_spend),
                high_risk_impact="+%0.0f pts" % supplier_improvement,
                executive_snapshot_icon=_info_icon(snapshot_reason, "executive_snapshot"),
                business_impact_icon=_info_icon(compliance_reason, "business_impact"),
                fastest_path_icon=_info_icon(evidence_path_reason, "fastest_improvement_path"),
                forecast_next_expiries="".join(next_expiries_html),
                forecast_risk_supplier=html_escape(top_missing_partner["name"]) if top_missing_partner else "No high-risk supplier identified",
                forecast_risk_spend=_money(top_missing_partner["spend"]) if top_missing_partner else _money(0.0),
                forecast_movement_period=html_escape(latest_movement_period),
                forecast_movement_color="#16a34a" if latest_movement >= 0 else "#d94b4b",
                forecast_movement_text="%+0.0f points" % latest_movement,
                hero_context_html=hero_context_html,
            )
            dashboard.business_impact_html = """
                <div style="display:grid;gap:10px;">
                    <div style="font-size:14px;font-weight:800;color:#1f2d3d;display:flex;align-items:center;gap:4px;">Business Impact{business_impact_icon}</div>
                    <div style="display:grid;gap:6px;">
                        <a href="#" class="bbbbee-dashboard-jump" data-target-button="action_open_assessments" title="{compliance_reason}" style="display:flex;justify-content:space-between;gap:12px;padding:8px 10px;border-radius:8px;background:#f3f6fb;font-size:13px;color:#52627c;text-decoration:none;cursor:pointer;">
                            <span>Compliance Risk</span><strong style="color:#1f2d3d;">{risk_level}</strong>
                        </a>
                        <a href="#" class="bbbbee-dashboard-jump" data-target-button="action_open_missing_evidence_lines" title="{missing_reason}" style="display:flex;justify-content:space-between;gap:12px;padding:8px 10px;border-radius:8px;background:#f3f6fb;font-size:13px;color:#52627c;text-decoration:none;cursor:pointer;">
                            <span>Verification Gaps</span><strong style="color:#1f2d3d;">{missing_evidence_count}</strong>
                        </a>
                        <a href="#" class="bbbbee-dashboard-jump" data-target-button="action_open_high_risk_suppliers" title="{supplier_reason}" style="display:flex;justify-content:space-between;gap:12px;padding:8px 10px;border-radius:8px;background:#f3f6fb;font-size:13px;color:#52627c;text-decoration:none;cursor:pointer;">
                            <span>High-Risk Suppliers</span><strong style="color:#1f2d3d;">{high_risk_supplier_count}</strong>
                        </a>
                    </div>
                </div>
            """.format(
                business_impact_icon=business_impact_icon,
                compliance_reason=compliance_reason,
                missing_reason=missing_reason,
                supplier_reason=supplier_reason,
                risk_level=risk_level,
                missing_evidence_count=dashboard.missing_evidence_count,
                high_risk_supplier_count=dashboard.high_risk_supplier_count,
            )
            dashboard.fastest_path_html = """
                <div style="border-top:1px solid #e5e7eb;padding-top:10px;">
                    <div style="font-size:11px;font-weight:800;letter-spacing:0.03em;text-transform:uppercase;color:#2f5be3;margin-bottom:8px;display:flex;align-items:center;gap:4px;">Fastest Improvement Path{fastest_path_icon}</div>
                    <div style="display:grid;gap:6px;">
                        <a href="#" class="bbbbee-dashboard-jump" data-target-button="action_open_missing_evidence_lines" title="{evidence_path_reason}" style="display:flex;justify-content:space-between;gap:12px;padding:8px 10px;border-radius:8px;background:#f3f6fb;font-size:13px;color:#52627c;text-decoration:none;cursor:pointer;">
                            <span>Resolve {missing_evidence_count} Verification Gaps</span><strong style="color:#1f2d3d;">+{evidence_improvement:.0f} pts</strong>
                        </a>
                        <a href="#" class="bbbbee-dashboard-jump" data-target-button="action_open_supplier_profiles" title="{supplier_mix_reason}" style="display:flex;justify-content:space-between;gap:12px;padding:8px 10px;border-radius:8px;background:#f3f6fb;font-size:13px;color:#52627c;text-decoration:none;cursor:pointer;">
                            <span>Improve High-Risk Supplier Mix</span><strong style="color:#1f2d3d;">+{supplier_improvement:.0f} pts</strong>
                        </a>
                    </div>
                </div>
            """.format(
                fastest_path_icon=fastest_path_icon,
                evidence_path_reason=evidence_path_reason,
                supplier_mix_reason=supplier_mix_reason,
                missing_evidence_count=dashboard.missing_evidence_count,
                evidence_improvement=evidence_improvement,
                supplier_improvement=supplier_improvement,
            )
            dashboard.forecast_html = """
                <div style="display:grid;gap:8px;">
                    <div>
                        <div style="font-size:11px;font-weight:700;color:#52627c;margin-bottom:6px;">Next Expiries</div>
                        {forecast_next_expiries}
                    </div>
                    <div>
                        <div style="font-size:11px;font-weight:700;color:#52627c;margin-bottom:6px;">Top Risk Supplier</div>
                        <div style="padding:8px 10px;border-radius:8px;background:#f3f6fb;font-size:12px;color:#52627c;">
                            <strong style="color:#1f2d3d;display:block;">{forecast_risk_supplier}</strong>
                            <span>{forecast_risk_spend} exposed to missing evidence</span>
                        </div>
                    </div>
                    <div>
                        <div style="font-size:11px;font-weight:700;color:#52627c;margin-bottom:6px;">Recent Score Movement</div>
                        <div style="padding:8px 10px;border-radius:8px;background:#f3f6fb;font-size:12px;color:#52627c;display:flex;justify-content:space-between;gap:10px;">
                            <span>{forecast_movement_period}</span>
                            <strong style="color:{forecast_movement_color};">{forecast_movement_text} since last sync</strong>
                        </div>
                    </div>
                </div>
            """.format(
                forecast_next_expiries="".join(next_expiries_html),
                forecast_risk_supplier=html_escape(top_missing_partner["name"]) if top_missing_partner else "No high-risk supplier identified",
                forecast_risk_spend=_money(top_missing_partner["spend"]) if top_missing_partner else _money(0.0),
                forecast_movement_period=html_escape(latest_movement_period),
                forecast_movement_color="#16a34a" if latest_movement >= 0 else "#d94b4b",
                forecast_movement_text="%+0.0f points" % latest_movement,
            )
            dashboard.blocking_html = """
                <div style="border-top:1px solid #e5e7eb;padding-top:10px;">
                    <div style="font-size:11px;font-weight:800;letter-spacing:0.03em;text-transform:uppercase;color:#2f5be3;margin-bottom:8px;">What&apos;s Blocking Compliance</div>
                    <div style="display:grid;gap:6px;">
                        <div style="display:flex;justify-content:space-between;gap:12px;padding:8px 10px;border-radius:8px;background:#f8fafc;font-size:13px;color:#52627c;">
                            <span>Missing supplier certificates</span><strong style="color:#1f2d3d;">{missing_certificate_impact}</strong>
                        </div>
                        <div style="display:flex;justify-content:space-between;gap:12px;padding:8px 10px;border-radius:8px;background:#f8fafc;font-size:13px;color:#52627c;">
                            <span>Unverified spend</span><strong style="color:#1f2d3d;">{verification_gap_spend_text}</strong>
                        </div>
                        <div style="display:flex;justify-content:space-between;gap:12px;padding:8px 10px;border-radius:8px;background:#f8fafc;font-size:13px;color:#52627c;">
                            <span>High-risk suppliers</span><strong style="color:#1f2d3d;">{high_risk_impact}</strong>
                        </div>
                    </div>
                    <div style="font-size:12px;color:#64748b;margin-top:8px;">Next action: fix verification gaps first, then recalculate the scorecard.</div>
                </div>
            """.format(
                missing_certificate_impact="+%0.0f pts" % evidence_improvement,
                verification_gap_spend_text=_money(verification_gap_spend),
                high_risk_impact="+%0.0f pts" % supplier_improvement,
            )
            dashboard.help_html = ""
            dashboard.info_html = _info_page_html(info_key) if info_key else ""
            visual_html = """
                <div style="margin:6px 0 14px;color:#4d5b74;font-size:13px;">
                    <strong>Period:</strong> %s
                </div>
                <div style="display:grid;gap:10px;">
                    <div style="border:1px solid #dde2ea;border-radius:8px;padding:10px 12px;background:#fff;">
                        <div style="display:flex;justify-content:space-between;gap:12px;margin-bottom:8px;font-size:13px;">
                            <span>Current Period Score%s</span><strong>%0.1f%%</strong>
                        </div>
                        <div style="height:10px;background:#edf1f6;border-radius:999px;overflow:hidden;">
                            <div style="height:100%%;width:%0.1f%%;%s"></div>
                        </div>
                        <div style="font-size:12px;color:#64748b;margin-top:6px;">This period&apos;s score against the target compliance threshold.</div>
                    </div>
                    <div style="border:1px solid #dde2ea;border-radius:8px;padding:10px 12px;background:#fff;">
                        <div style="display:flex;justify-content:space-between;gap:12px;margin-bottom:8px;font-size:13px;">
                            <span>Supplier Compliance Health%s</span><strong>%0.1f%%</strong>
                        </div>
                        <div style="height:10px;background:#edf1f6;border-radius:999px;overflow:hidden;">
                            <div style="height:100%%;width:%0.1f%%;%s"></div>
                        </div>
                        <div style="font-size:12px;color:#64748b;margin-top:6px;">More valid certificates means more spend can be verified.</div>
                    </div>
                    <div style="border:1px solid #dde2ea;border-radius:8px;padding:10px 12px;background:#fff;">
                        <div style="display:flex;justify-content:space-between;gap:12px;margin-bottom:8px;font-size:13px;">
                            <span>Spend At Risk%s</span><strong>%0.1f%%</strong>
                        </div>
                        <div style="height:10px;background:#edf1f6;border-radius:999px;overflow:hidden;">
                            <div style="height:100%%;width:%0.1f%%;%s"></div>
                        </div>
                        <div style="font-size:12px;color:#64748b;margin-top:6px;">Gaps here reduce recognised spend and increase verification risk.</div>
                    </div>
                </div>
                <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px;margin-top:14px;">
                </div>
            """ % (
                period_name,
                _info_icon(current_score_reason, "current_period_score"),
                dashboard.achieved_percentage,
                achieved_pct,
                "background:linear-gradient(90deg,#1fba63,#45d086);" if achieved_class == "good" else "background:linear-gradient(90deg,#f0a21a,#f5be4f);",
                _info_icon(supplier_health_reason, "supplier_compliance_health"),
                dashboard.compliance_rate,
                compliance_pct,
                "background:linear-gradient(90deg,#1fba63,#45d086);" if compliance_class == "good" else "background:linear-gradient(90deg,#f0a21a,#f5be4f);",
                _info_icon(spend_at_risk_reason, "spend_at_risk"),
                dashboard.evidence_gap_rate,
                gap_pct,
                "background:linear-gradient(90deg,#1fba63,#45d086);" if gap_class == "good" else "background:linear-gradient(90deg,#d94b4b,#ee7272);",
            )

            def _legend_row(label, color, value_text):
                return (
                    "<div style='display:flex;justify-content:space-between;gap:10px;align-items:center;"
                    "font-size:12px;color:#4d5b74;line-height:1.2;'>"
                    "<span><span style='color:%s;font-size:14px;vertical-align:middle;'>●</span> %s</span>"
                    "<strong style='color:#1f2d3d;'>%s</strong>"
                    "</div>"
                ) % (color, label, value_text)

            def _pie_card(title, description, segments, legend_rows, size=96, target_button=None, info_text=None, info_key=None):
                total = sum(value for _, value, _, _ in segments) or 1.0
                start = 0.0
                parts = []
                for _, value, color, _ in segments:
                    slice_pct = (value / total) * 100.0
                    parts.append("%s %0.1f%% %0.1f%%" % (color, start, start + slice_pct))
                    start += slice_pct
                legend_html = "".join(legend_rows)
                title_icon = _info_icon(info_text, info_key) if info_text else ""
                card_html = """
                    <div style="border:1px solid #dbe2ee;border-radius:10px;padding:12px 14px;background:#fff;min-height:150px;">
                        <div style="font-size:13px;font-weight:700;color:#1f2d3d;margin-bottom:4px;display:flex;align-items:center;gap:4px;">%s%s</div>
                        <div style="font-size:12px;color:#52627c;margin-bottom:10px;">%s</div>
                        <div style="display:flex;align-items:center;gap:12px;">
                            <div style="width:%spx;height:%spx;border-radius:50%%;background:conic-gradient(%s);flex:0 0 %spx;"></div>
                            <div style="flex:1;display:grid;gap:4px;">%s</div>
                        </div>
                    </div>
                """ % (
                    title,
                    title_icon,
                    description,
                    size,
                    size,
                    ", ".join(parts) if parts else "#e5e7eb 0 100%",
                    size,
                    legend_html,
                )
                if target_button:
                    return '<a href="#" class="bbbbee-dashboard-jump" data-target-button="%s" style="display:block;text-decoration:none;color:inherit;">%s</a>' % (target_button, card_html)
                return card_html

            def _bar_card(title, description, bars, legend_rows, target_button=None, info_text=None, info_key=None):
                bar_html = []
                for label, value, color in bars:
                    bar_html.append(
                        """
                        <div style='display:grid;gap:4px;'>
                            <div style='display:flex;justify-content:space-between;gap:10px;font-size:12px;color:#52627c;'>
                                <span>%s</span><strong style='color:#1f2d3d;'>%0.1f%%</strong>
                            </div>
                            <div style='height:10px;background:#edf1f6;border-radius:999px;overflow:hidden;'>
                                <div style='height:100%%;width:%0.1f%%;background:%s;'></div>
                            </div>
                        </div>
                        """ % (label, value, max(0.0, min(100.0, value)), color)
                    )
                title_icon = _info_icon(info_text, info_key) if info_text else ""
                card_html = """
                    <div style="border:1px solid #dbe2ee;border-radius:10px;padding:12px 14px;background:#fff;min-height:150px;">
                        <div style="font-size:13px;font-weight:700;color:#1f2d3d;margin-bottom:4px;display:flex;align-items:center;gap:4px;">%s%s</div>
                        <div style="font-size:12px;color:#52627c;margin-bottom:10px;">%s</div>
                        <div style="display:grid;gap:8px;">%s</div>
                        <div style="border-top:1px solid #eef2f7;margin-top:10px;padding-top:8px;display:grid;gap:4px;">%s</div>
                    </div>
                """ % (title, title_icon, description, "".join(bar_html), "".join(legend_rows))
                if target_button:
                    return '<a href="#" class="bbbbee-dashboard-jump" data-target-button="%s" style="display:block;text-decoration:none;color:inherit;">%s</a>' % (target_button, card_html)
                return card_html

            spend_classification_segments = [
                ("Included", classification_totals["included"], "#1fba63", _money(classification_totals["included"])),
                ("Review", classification_totals["review"], "#f0a21a", _money(classification_totals["review"])),
                ("Excluded", classification_totals["excluded"], "#d94b4b", _money(classification_totals["excluded"])),
            ]
            evidence_status_segments = [
                ("Valid", evidence_totals["valid"], "#1fba63", _money(evidence_totals["valid"])),
                ("Review required", evidence_totals["review_required"], "#f0a21a", _money(evidence_totals["review_required"])),
                ("Missing", evidence_totals["missing"], "#d94b4b", _money(evidence_totals["missing"])),
                ("Expired", evidence_totals["expired"], "#b91c1c", _money(evidence_totals["expired"])),
            ]
            certificate_status_segments = [
                ("Valid", certificate_totals["valid"], "#1fba63", str(certificate_totals["valid"])),
                ("Expiring", certificate_totals["expiring_soon"], "#f0a21a", str(certificate_totals["expiring_soon"])),
                ("Missing", certificate_totals["missing"], "#d94b4b", str(certificate_totals["missing"])),
                ("Expired", certificate_totals["expired"], "#b91c1c", str(certificate_totals["expired"])),
            ]
            assessment_trend_rows = assessment_history[-6:]
            assessment_trend_bars = [
                (record.measurement_period_id.name, record.achieved_percentage, "#2f5be3")
                for record in assessment_trend_rows
            ] or [("No assessment data", 0.0, "#d6e0f5")]
            visual_html += """
                <div style="margin-top:14px;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;">
                    %s
                    %s
                    %s
                    %s
                </div>
            """ % (
                _pie_card(
                    "Verification-Ready Spend",
                    "Measured spend split between ready, review, and excluded lines.",
                    spend_classification_segments,
                    [
                        _legend_row("Verification-ready", "#1fba63", _money(classification_totals["included"])),
                        _legend_row("Review required", "#f0a21a", _money(classification_totals["review"])),
                        _legend_row("Excluded", "#d94b4b", _money(classification_totals["excluded"])),
                    ],
                    target_button="action_open_chart_spend_classification",
                    info_text="The safe portion of your procurement spend backed by valid, certified compliance documentation.",
                    info_key="verification_ready_spend",
                ),
                _pie_card(
                    "Spend At Risk",
                    "Spend lines grouped by evidence status so the user can see what is safe, pending, or exposed.",
                    evidence_status_segments,
                    [
                        _legend_row("Valid", "#1fba63", _money(evidence_totals["valid"])),
                        _legend_row("Review required", "#f0a21a", _money(evidence_totals["review_required"])),
                        _legend_row("Missing", "#d94b4b", _money(evidence_totals["missing"])),
                        _legend_row("Expired", "#b91c1c", _money(evidence_totals["expired"])),
                    ],
                    target_button="action_open_chart_evidence_status",
                    info_text="Rand value vulnerable to auditor rejection due to missing or expired supplier paperwork.",
                    info_key="spend_at_risk",
                ),
                _pie_card(
                    "Supplier Compliance Health",
                    "Supplier certificates by record state. More valid records means less verification risk.",
                    certificate_status_segments,
                    [
                        _legend_row("Valid", "#1fba63", str(certificate_totals["valid"])),
                        _legend_row("Expiring soon", "#f0a21a", str(certificate_totals["expiring_soon"])),
                        _legend_row("Missing", "#d94b4b", str(certificate_totals["missing"])),
                        _legend_row("Expired", "#b91c1c", str(certificate_totals["expired"])),
                    ],
                    target_button="action_open_chart_certificate_status",
                    info_text="The percentage of active vendors in your supply chain with up-to-date, valid B-BBEE certificates.",
                    info_key="supplier_compliance_health",
                ),
                _bar_card(
                    "Current Period Score",
                    "Latest assessment by measurement period. This bar shows the current period score.",
                    assessment_trend_bars,
                    [
                        _legend_row("Current Period Progress Score", "#2f5be3", "%0.1f%%" % dashboard.achieved_percentage),
                        _legend_row("Target Score Threshold", "#64748b", "%0.1f%%" % dashboard.target_percentage),
                    ],
                    target_button="action_open_chart_assessment_trend",
                    info_text="Your accumulated point milestones measured against your target regulatory framework.",
                    info_key="current_period_score",
                ),
            )
            dashboard.visual_html = visual_html

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

    def action_open_spend_batches(self):
        return self._open_action("bbbbee_procurement.action_bbbbee_spend_batch")

    def action_open_assessments(self):
        return self._open_action("bbbbee_procurement.action_bbbbee_scorecard_assessment")

    def action_open_evidence_packs(self):
        return self._open_action("bbbbee_procurement.action_bbbbee_evidence_pack")

    def action_open_import_spend(self):
        action = self._open_action("bbbbee_procurement.action_bbbbee_import_spend_wizard")
        action["context"] = {
            "default_company_id": self.company_id.id,
            "default_measurement_period_id": self.measurement_period_id.id,
        }
        return action

    def action_open_generate_evidence(self):
        action = self._open_action("bbbbee_procurement.action_bbbbee_generate_evidence_pack_wizard")
        action["context"] = {
            "default_company_id": self.company_id.id,
            "default_measurement_period_id": self.measurement_period_id.id,
        }
        return action

    def action_open_recalculate_scorecard(self):
        action = self._open_action("bbbbee_procurement.action_bbbbee_recalculate_scorecard_wizard")
        assessment = False
        if self.measurement_period_id:
            assessment = self.env["bbbbee.scorecard.assessment"].search(
                [("measurement_period_id", "=", self.measurement_period_id.id)],
                limit=1,
            )
            if not assessment and self.measurement_period_id.active_rule_set_id:
                assessment = self.env["bbbbee.scorecard.assessment"].create(
                    {
                        "name": "Assessment - %s" % self.measurement_period_id.name,
                        "measurement_period_id": self.measurement_period_id.id,
                        "rule_set_id": self.measurement_period_id.active_rule_set_id.id,
                        "spend_batch_ids": [
                            (
                                6,
                                0,
                                self.env["bbbbee.spend.batch"]
                                .search([("measurement_period_id", "=", self.measurement_period_id.id)])
                                .ids,
                            )
                        ],
                    }
                )
        if assessment:
            action["context"] = {"default_assessment_id": assessment.id}
        return action

    def _period_spend_domain(self):
        if not self.measurement_period_id:
            return [("id", "=", 0)]
        return [("batch_id.measurement_period_id", "=", self.measurement_period_id.id)]

    def _period_assessment_domain(self):
        if not self.measurement_period_id:
            return [("id", "=", 0)]
        return [("measurement_period_id", "=", self.measurement_period_id.id)]

    def action_open_chart_spend_classification(self):
        action = self._open_action("bbbbee_procurement.action_bbbbee_chart_spend_classification")
        action["domain"] = self._period_spend_domain()
        return action

    def action_open_chart_evidence_status(self):
        action = self._open_action("bbbbee_procurement.action_bbbbee_chart_evidence_status")
        action["domain"] = self._period_spend_domain()
        return action

    def action_open_chart_certificate_status(self):
        action = self._open_action("bbbbee_procurement.action_bbbbee_chart_certificate_status")
        return action

    def action_load_starter_demo(self):
        self.ensure_one()
        today = fields.Date.context_today(self)
        partner = self.env["res.partner"].search(
            [("name", "=", "B-good Starter Supplier"), ("company_id", "in", [False, self.company_id.id])],
            limit=1,
        )
        if not partner:
            partner = self.env["res.partner"].create(
                {"name": "B-good Starter Supplier", "supplier_rank": 1, "email": "supplier@example.com"}
            )
        profile = self.env["bbbbee.supplier.profile"].search([("partner_id", "=", partner.id)], limit=1)
        if not profile:
            profile = self.env["bbbbee.supplier.profile"].create(
                {
                    "partner_id": partner.id,
                    "bbbbee_level": "2",
                    "recognition_percentage": 125.0,
                    "black_ownership_percentage": 51.0,
                    "black_women_ownership_percentage": 20.0,
                    "empowering_supplier_status": "yes",
                }
            )
        certificate = self.env["bbbbee.supplier.certificate"].search(
            [("profile_id", "=", profile.id), ("certificate_number", "=", "STARTER-001")],
            limit=1,
        )
        if not certificate:
            certificate = self.env["bbbbee.supplier.certificate"].create(
                {
                    "profile_id": profile.id,
                    "certificate_type": "certificate",
                    "certificate_number": "STARTER-001",
                    "issue_date": today,
                    "expiry_date": today + timedelta(days=180),
                    "attachment_id": self._ensure_demo_attachment().id,
                }
            )
        rule_set = self._get_or_create_rule_set()
        period = self.env["bbbbee.measurement.period"].search(
            [("company_id", "=", self.company_id.id), ("name", "=", self._starter_period_label())],
            limit=1,
        )
        if not period:
            period = self.env["bbbbee.measurement.period"].create(
                {
                    "name": self._starter_period_label(),
                    "company_id": self.company_id.id,
                    "date_start": today.replace(month=1, day=1),
                    "date_end": today.replace(month=12, day=31),
                    "active_rule_set_id": rule_set.id,
                }
            )
        batch = self.env["bbbbee.spend.batch"].search([("measurement_period_id", "=", period.id)], limit=1)
        if not batch:
            batch = self.env["bbbbee.spend.batch"].create(
                {
                    "name": "Starter Spend Batch - %s" % period.name,
                    "measurement_period_id": period.id,
                    "company_id": self.company_id.id,
                }
            )
        line = self.env["bbbbee.spend.line"].search([("batch_id", "=", batch.id), ("partner_id", "=", partner.id)], limit=1)
        if not line:
            self.env["bbbbee.spend.line"].create(
                {
                    "batch_id": batch.id,
                    "partner_id": partner.id,
                    "move_id": False,
                    "invoice_date": today,
                    "untaxed_amount": 100000.0,
                    "excluded_amount": 0.0,
                    "recognition_percentage": profile.recognition_percentage,
                    "classification": "included",
                    "evidence_status": "valid",
                }
            )
        assessment = self.env["bbbbee.scorecard.assessment"].search([("measurement_period_id", "=", period.id)], limit=1)
        if not assessment:
            assessment = self.env["bbbbee.scorecard.assessment"].create(
                {
                    "name": "Starter Assessment - %s" % period.name,
                    "measurement_period_id": period.id,
                    "rule_set_id": rule_set.id,
                    "spend_batch_ids": [(6, 0, [batch.id])],
                }
            )
        pack = self.env["bbbbee.evidence.pack"].search([("measurement_period_id", "=", period.id)], limit=1)
        if not pack:
            pack = self.env["bbbbee.evidence.pack"].create(
                {
                    "name": "Starter Evidence Pack - %s" % period.name,
                    "measurement_period_id": period.id,
                    "assessment_id": assessment.id,
                    "state": "generated",
                }
            )
        if not pack.item_ids:
            self.env["bbbbee.evidence.item"].create(
                {
                    "pack_id": pack.id,
                    "name": "Starter summary",
                    "item_type": "summary",
                    "note": "Sample data loaded for first-time walkthrough.",
                }
            )
        return self.action_open_dashboard_home()

    def action_open_expiring_certificates(self):
        action = self._open_action("bbbbee_procurement.action_bbbbee_supplier_certificate")
        today = fields.Date.context_today(self)
        window_days = max(int(self.expiry_window_days or 30), 1)
        action["domain"] = [
            ("active", "=", True),
            ("expiry_date", ">=", today),
            ("expiry_date", "<=", today + timedelta(days=window_days)),
        ]
        return action

    def action_open_chart_assessment_trend(self):
        action = self._open_action("bbbbee_procurement.action_bbbbee_chart_assessment_trend")
        action["domain"] = self._period_assessment_domain()
        return action

    def action_open_missing_evidence_lines(self):
        action = self._open_action("bbbbee_procurement.action_bbbbee_spend_line")
        action["domain"] = self._period_spend_domain() + [("evidence_status", "in", ("missing", "review_required", "expired"))]
        return action

    def action_open_high_risk_suppliers(self):
        supplier_profiles = self.env["bbbbee.supplier.profile"].search([])
        risk_service = self.env["bbbbee.supplier.risk.service"]
        high_risk_partner_ids = [
            profile.partner_id.id
            for profile in supplier_profiles
            if risk_service.get_risk_level(profile.partner_id) == "high"
        ]
        action = self._open_action("bbbbee_procurement.action_bbbbee_supplier_profile")
        action["domain"] = [("partner_id", "in", high_risk_partner_ids)] if high_risk_partner_ids else [("id", "=", 0)]
        return action

    def _open_info_action(self, info_key):
        action = self._open_action("bbbbee_procurement.action_bbbbee_dashboard_info")
        action["context"] = dict(self.env.context, dashboard_info_key=info_key, default_info_key=info_key)
        return action

    def action_open_info_executive_snapshot(self):
        return self._open_info_action("executive_snapshot")

    def action_open_info_business_impact(self):
        return self._open_info_action("business_impact")

    def action_open_info_fastest_improvement_path(self):
        return self._open_info_action("fastest_improvement_path")

    def action_open_info_in_scope_spend(self):
        return self._open_info_action("in_scope_spend")

    def action_open_info_verification_ready_spend(self):
        return self._open_info_action("verification_ready_spend")

    def action_open_info_current_period_score(self):
        return self._open_info_action("current_period_score")

    def action_open_info_supplier_compliance_health(self):
        return self._open_info_action("supplier_compliance_health")

    def action_open_info_spend_at_risk(self):
        return self._open_info_action("spend_at_risk")

    def action_open_info_bee_level(self):
        return self._open_info_action("bee_level")

    def action_open_dashboard_home(self):
        action = self._open_action("bbbbee_procurement.action_bbbbee_dashboard")
        action["context"] = {}
        return action
