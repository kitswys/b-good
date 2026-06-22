from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class BbbbeeComplianceAlertPolicy(models.Model):
    _name = "bbbbee.compliance.alert.policy"
    _description = "B-BBEE Compliance Alert Policy"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(required=True, default="Default Alert Policy", tracking=True)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company)
    active = fields.Boolean(default=True)
    reminder_days = fields.Char(
        default="30,14,7",
        help="Comma-separated reminder windows in days before expiry. Example: 30,14,7",
        tracking=True,
    )
    activity_user_id = fields.Many2one(
        "res.users",
        string="Activity Assignee",
        help="User who receives generated expiry activities.",
        tracking=True,
    )
    email_template_id = fields.Many2one(
        "mail.template",
        string="Expiry Email Template",
        domain=[("model_id.model", "=", "bbbbee.supplier.certificate")],
        help="Email template used for expiry reminders.",
        tracking=True,
    )

    _sql_constraints = [
        ("company_policy_unique", "unique(company_id)", "Each company can have only one alert policy."),
    ]

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

    def _get_reminder_windows(self):
        self.ensure_one()
        windows = []
        for token in (self.reminder_days or "").split(","):
            token = token.strip()
            if not token:
                continue
            try:
                value = int(token)
            except ValueError as exc:
                raise ValidationError("Reminder days must contain only integers separated by commas.") from exc
            if value > 0 and value not in windows:
                windows.append(value)
        return sorted(windows, reverse=True)

    @classmethod
    def _create_default_record_if_missing(cls, env, company):
        policy = env[cls._name].search([("company_id", "=", company.id)], limit=1)
        if not policy:
            policy = env[cls._name].create(
                {
                    "name": "Default Alert Policy - %s" % company.display_name,
                    "company_id": company.id,
                }
            )
        return policy

    def _send_expiry_reminders(self):
        AlertLog = self.env["bbbbee.compliance.alert.log"]
        Certificate = self.env["bbbbee.supplier.certificate"]
        today = fields.Date.context_today(self)
        for policy in self:
            if not policy.active:
                continue
            reminder_windows = policy._get_reminder_windows()
            if not reminder_windows:
                continue
            max_window = max(reminder_windows)
            certificates = Certificate.search(
                [
                    ("active", "=", True),
                    ("expiry_date", "!=", False),
                    ("expiry_date", ">=", today),
                    ("expiry_date", "<=", today + timedelta(days=max_window)),
                ]
            )
            for certificate in certificates:
                days_remaining = (certificate.expiry_date - today).days if certificate.expiry_date else None
                if days_remaining is None or days_remaining not in reminder_windows:
                    continue
                if AlertLog.search_count(
                    [
                        ("certificate_id", "=", certificate.id),
                        ("reminder_days", "=", days_remaining),
                        ("alert_date", "=", today),
                    ]
                ):
                    continue
                AlertLog.create(
                    {
                        "company_id": policy.company_id.id,
                        "certificate_id": certificate.id,
                        "reminder_days": days_remaining,
                        "alert_date": today,
                    }
                )
                template = policy.email_template_id or self.env.ref(
                    "bbbbee_procurement.mail_template_certificate_expiring",
                    raise_if_not_found=False,
                )
                if template and certificate.partner_id.email:
                    template.send_mail(certificate.id, force_send=True)
                if policy.activity_user_id:
                    certificate.activity_schedule(
                        "mail.mail_activity_data_todo",
                        user_id=policy.activity_user_id.id,
                        summary="B-BBEE certificate expires in %s days" % days_remaining,
                        note="Certificate %s for %s expires on %s."
                        % (certificate.certificate_number or certificate.id, certificate.partner_id.display_name, certificate.expiry_date),
                    )

    def cron_send_expiry_reminders(self):
        policies = self.search([])
        if not policies:
            companies = self.env["res.company"].search([])
            policies = self.browse()
            for company in companies:
                policies |= self._create_default_record_if_missing(self.env, company)
        policies._send_expiry_reminders()


class BbbbeeComplianceAlertLog(models.Model):
    _name = "bbbbee.compliance.alert.log"
    _description = "B-BBEE Compliance Alert Log"
    _order = "alert_date desc, id desc"

    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company)
    certificate_id = fields.Many2one("bbbbee.supplier.certificate", required=True, ondelete="cascade")
    reminder_days = fields.Integer(required=True)
    alert_date = fields.Date(required=True, default=fields.Date.context_today)

    _sql_constraints = [
        (
            "alert_log_unique",
            "unique(certificate_id, reminder_days, alert_date)",
            "An alert has already been logged for this certificate, reminder window, and date.",
        ),
    ]
