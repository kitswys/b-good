from odoo import api, fields, models
from odoo.exceptions import UserError


class BbbbeeSupplierProfile(models.Model):
    _name = "bbbbee.supplier.profile"
    _description = "Supplier B-BBEE Compliance Profile"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "partner_id"

    partner_id = fields.Many2one(
        "res.partner",
        required=True,
        domain=[("supplier_rank", ">", 0)],
        tracking=True,
        help="Select the supplier/vendor this B-BBEE profile applies to.",
    )
    bbbbee_level = fields.Selection(
        [
            ("1", "Level 1"),
            ("2", "Level 2"),
            ("3", "Level 3"),
            ("4", "Level 4"),
            ("5", "Level 5"),
            ("6", "Level 6"),
            ("7", "Level 7"),
            ("8", "Level 8"),
            ("non_compliant", "Non-compliant"),
            ("unknown", "Unknown"),
        ],
        default="unknown",
        tracking=True,
        help="Supplier B-BBEE contributor level from the latest valid certificate or affidavit.",
    )
    recognition_percentage = fields.Float(
        default=0.0,
        tracking=True,
        help="Recognition percentage used when calculating recognised procurement spend.",
    )
    black_ownership_percentage = fields.Float(help="Black ownership percentage stated in supplier evidence.")
    black_women_ownership_percentage = fields.Float(help="Black women ownership percentage from supplier evidence.")
    empowering_supplier_status = fields.Selection(
        [("yes", "Yes"), ("no", "No"), ("unknown", "Unknown")],
        default="unknown",
        tracking=True,
        help="Whether supplier qualifies as an empowering supplier.",
    )
    certificate_ids = fields.One2many(
        "bbbbee.supplier.certificate",
        "profile_id",
        string="Certificates and Affidavits",
        help="Attach and manage compliance evidence records for this supplier.",
    )
    active_certificate_id = fields.Many2one(
        "bbbbee.supplier.certificate",
        compute="_compute_active_certificate",
        store=True,
    )
    compliance_status = fields.Selection(
        [
            ("valid", "Valid"),
            ("expiring_soon", "Expiring Soon"),
            ("expired", "Expired"),
            ("missing", "Missing"),
            ("superseded", "Superseded"),
        ],
        compute="_compute_compliance_status",
        store=True,
        tracking=True,
        help="Overall evidence health derived from current certificate records.",
    )
    compliance_status_badge_html = fields.Html(compute="_compute_compliance_status_badge_html", sanitize=False)
    active_certificate_link_html = fields.Html(compute="_compute_active_certificate_link_html", sanitize=False)

    _sql_constraints = [
        (
            "partner_profile_unique",
            "unique(partner_id)",
            "Each supplier can only have one active B-BBEE profile.",
        )
    ]

    @api.depends("certificate_ids.state", "certificate_ids.expiry_date")
    def _compute_active_certificate(self):
        for profile in self:
            profile.active_certificate_id = profile.certificate_ids.filtered(
                lambda certificate: certificate.state in ("valid", "expiring_soon")
            )[:1]

    @api.depends("active_certificate_id.state", "certificate_ids.state")
    def _compute_compliance_status(self):
        for profile in self:
            if profile.active_certificate_id:
                profile.compliance_status = profile.active_certificate_id.state
            elif profile.certificate_ids:
                profile.compliance_status = "expired"
            else:
                profile.compliance_status = "missing"

    @api.depends("compliance_status")
    def _compute_compliance_status_badge_html(self):
        status_map = {
            "valid": ("#eef7ef", "#166534", "Valid"),
            "expiring_soon": ("#fcf6e8", "#7c5c1d", "Expiring Soon"),
            "expired": ("#fdecec", "#991b1b", "Expired"),
            "missing": ("#fff4f4", "#991b1b", "Missing"),
            "superseded": ("#f3f4f6", "#475569", "Superseded"),
        }
        for profile in self:
            bg, fg, label = status_map.get(profile.compliance_status or "missing")
            profile.compliance_status_badge_html = (
                '<span class="badge badge-pill bbbbee-pill-badge" '
                'style="background:%s;color:%s;display:inline-flex;align-items:center;justify-content:center;'
                'min-width:96px;padding:4px 10px;border-radius:999px;font-size:11px;font-weight:700;'
                'letter-spacing:0.02em;text-transform:uppercase;">%s</span>'
                % (bg, fg, label)
            )

    @api.depends("active_certificate_id", "active_certificate_id.attachment_id")
    def _compute_active_certificate_link_html(self):
        for profile in self:
            certificate = profile.active_certificate_id
            if certificate and certificate.attachment_id:
                profile.active_certificate_link_html = (
                    '<a class="bbbbee-link-chip bbbbee-link-chip-secondary" '
                    'href="/web/content/%s?download=false" target="_blank" rel="noopener noreferrer">'
                    '📄 View Certificate Attachment</a>' % certificate.attachment_id.id
                )
            elif certificate:
                profile.active_certificate_link_html = (
                    '<a class="bbbbee-link-chip bbbbee-link-chip-secondary" '
                    'href="/web#id=%s&model=bbbbee.supplier.certificate&view_type=form">'
                    '📄 Open Active Certificate</a>' % certificate.id
                )
            else:
                profile.active_certificate_link_html = '<span class="text-muted small">No active certificate</span>'

    def name_create(self, name):
        raise UserError(
            "Create the supplier profile from Supplier Profiles first, then select it here."
        )

    def action_open_bulk_certificate_wizard(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Bulk Upload Evidence",
            "res_model": "bbbbee.certificate.bulk.upload.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_profile_id": self.id, "default_company_id": self.env.company.id},
        }
