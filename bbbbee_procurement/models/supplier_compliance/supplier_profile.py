from odoo import api, fields, models


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
    )
    recognition_percentage = fields.Float(default=0.0, tracking=True)
    black_ownership_percentage = fields.Float(tracking=True)
    black_women_ownership_percentage = fields.Float(tracking=True)
    empowering_supplier_status = fields.Selection(
        [("yes", "Yes"), ("no", "No"), ("unknown", "Unknown")],
        default="unknown",
        tracking=True,
    )
    certificate_ids = fields.One2many(
        "bbbbee.supplier.certificate",
        "profile_id",
        string="Certificates and Affidavits",
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
    )

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
