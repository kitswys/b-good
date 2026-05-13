from datetime import timedelta

from odoo import api, fields, models


class BbbbeeSupplierCertificate(models.Model):
    _name = "bbbbee.supplier.certificate"
    _description = "Supplier B-BBEE Certificate or Affidavit"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "expiry_date desc, id desc"

    profile_id = fields.Many2one("bbbbee.supplier.profile", required=True, ondelete="cascade")
    partner_id = fields.Many2one(related="profile_id.partner_id", store=True)
    certificate_type = fields.Selection(
        [("certificate", "Certificate"), ("affidavit", "Affidavit"), ("none", "None")],
        default="certificate",
        required=True,
        tracking=True,
    )
    certificate_number = fields.Char(tracking=True)
    issue_date = fields.Date(tracking=True)
    expiry_date = fields.Date(required=True, tracking=True)
    attachment_id = fields.Many2one("ir.attachment", string="Evidence Attachment")
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
    active = fields.Boolean(default=True)

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

    def action_supersede(self):
        self.write({"active": False})
