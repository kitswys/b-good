from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class BbbbeeSupplierCertificate(models.Model):
    _name = "bbbbee.supplier.certificate"
    _description = "Supplier B-BBEE Certificate or Affidavit"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "expiry_date desc, id desc"

    profile_id = fields.Many2one(
        "bbbbee.supplier.profile",
        required=True,
        ondelete="cascade",
        help="Supplier profile this certificate or affidavit belongs to.",
    )
    partner_id = fields.Many2one(related="profile_id.partner_id", store=True)
    certificate_type = fields.Selection(
        [("certificate", "Certificate"), ("affidavit", "Affidavit"), ("none", "None")],
        default="certificate",
        required=True,
        tracking=True,
        help="Choose whether this record is a certificate or affidavit.",
    )
    certificate_number = fields.Char(tracking=True, help="Reference number from the supplier's certificate/affidavit.")
    issue_date = fields.Date(tracking=True, help="Document issue date.")
    expiry_date = fields.Date(required=True, tracking=True, help="Document expiry date used for validity checks.")
    attachment_file = fields.Binary(
        string="Evidence File",
        help="Upload the actual certificate or affidavit file (PDF/image).",
    )
    attachment_filename = fields.Char(string="Filename")
    attachment_id = fields.Many2one(
        "ir.attachment",
        string="Evidence Attachment",
        help="Upload the actual certificate or affidavit file (PDF/image).",
    )
    tag_ids = fields.Many2many("bbbbee.document.tag", string="Tags")
    attachment_present = fields.Boolean(compute="_compute_attachment_present")
    attachment_marker_html = fields.Html(compute="_compute_attachment_present", sanitize=False)
    state = fields.Selection(
        [
            ("valid", "Valid"),
            ("expiring_soon", "Expiring Soon"),
            ("expired", "Expired"),
            ("missing", "Missing"),
            ("superseded", "Superseded"),
        ],
        compute="_compute_state",
        store=True,
        tracking=True,
    )
    state_badge_html = fields.Html(compute="_compute_state_badge_html", sanitize=False)
    active = fields.Boolean(default=True, help="Active certificates are considered for compliance status.")

    @api.depends("expiry_date", "attachment_id", "active")
    def _compute_state(self):
        today = fields.Date.context_today(self)
        for certificate in self:
            if not certificate.active:
                certificate.state = "superseded"
            elif not certificate.attachment_id:
                certificate.state = "missing"
            elif certificate.expiry_date < today:
                certificate.state = "expired"
            elif certificate.expiry_date <= today + timedelta(days=90):
                certificate.state = "expiring_soon"
            else:
                certificate.state = "valid"

    @api.depends("attachment_id", "attachment_file")
    def _compute_attachment_present(self):
        for certificate in self:
            certificate.attachment_present = bool(certificate.attachment_id or certificate.attachment_file)
            if certificate.attachment_present and certificate.attachment_id:
                certificate.attachment_marker_html = (
                    '<a class="bbbbee-link-chip bbbbee-link-chip-secondary" '
                    'href="/web/content/%s?download=false" target="_blank" rel="noopener noreferrer">'
                    '📄 View Certificate Attachment</a>' % certificate.attachment_id.id
                )
            elif certificate.attachment_present:
                certificate.attachment_marker_html = (
                    '<a class="bbbbee-link-chip bbbbee-link-chip-secondary" '
                    'href="/web#id=%s&model=bbbbee.supplier.certificate&view_type=form">'
                    '📄 View Certificate Attachment</a>' % certificate.id
                )
            else:
                certificate.attachment_marker_html = '<span class="text-muted small">No attachment uploaded</span>'

    @api.depends("state")
    def _compute_state_badge_html(self):
        state_map = {
            "valid": ("#eef7ef", "#166534", "Valid"),
            "expiring_soon": ("#fcf6e8", "#7c5c1d", "Expiring Soon"),
            "expired": ("#fdecec", "#991b1b", "Expired"),
            "missing": ("#fff4f4", "#991b1b", "Missing"),
            "superseded": ("#f3f4f6", "#475569", "Superseded"),
        }
        for certificate in self:
            bg, fg, label = state_map.get(certificate.state or "missing")
            certificate.state_badge_html = (
                '<span class="badge badge-pill bbbbee-pill-badge" style="background:%s;color:%s;display:inline-flex;'
                'align-items:center;justify-content:center;min-width:96px;padding:4px 10px;border-radius:999px;'
                'font-size:11px;font-weight:700;letter-spacing:0.02em;text-transform:uppercase;">%s</span>'
                % (bg, fg, label)
            )

    def _sync_attachment_record(self, file_data=None, file_name=None):
        for certificate in self:
            if not file_data and not certificate.attachment_id:
                continue
            attachment_vals = {
                "name": file_name or certificate.certificate_number or certificate.profile_id.partner_id.display_name,
                "type": "binary",
                "res_model": certificate._name,
                "res_id": certificate.id,
            }
            if file_data:
                attachment_vals["datas"] = file_data
            if certificate.attachment_id:
                certificate.attachment_id.write(attachment_vals)
            elif file_data:
                certificate.attachment_id = self.env["ir.attachment"].create(attachment_vals).id

    def action_supersede(self):
        self.write({"active": False})

    @api.constrains("issue_date", "expiry_date")
    def _check_issue_expiry_dates(self):
        for certificate in self:
            if certificate.issue_date and certificate.expiry_date and certificate.expiry_date < certificate.issue_date:
                raise ValidationError("Certificate expiry date must be on or after the issue date.")

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            if record.attachment_file:
                record._sync_attachment_record(record.attachment_file, record.attachment_filename)
        return records

    def write(self, vals):
        file_data = vals.get("attachment_file")
        file_name = vals.get("attachment_filename")
        result = super().write(vals)
        if file_data:
            self._sync_attachment_record(file_data, file_name)
        return result
