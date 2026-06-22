from odoo import api, fields, models


class BbbbeeCertificateBulkUploadWizardLine(models.TransientModel):
    _name = "bbbbee.certificate.bulk.upload.wizard.line"
    _table = "bbbbee_cert_bulk_upload_line"
    _description = "Bulk Upload Certificate Line"

    wizard_id = fields.Many2one("bbbbee.certificate.bulk.upload.wizard", required=True, ondelete="cascade")
    sequence = fields.Integer(default=10)
    certificate_type = fields.Selection(
        [("certificate", "Certificate"), ("affidavit", "Affidavit"), ("none", "None")],
        default="certificate",
        required=True,
    )
    certificate_number = fields.Char()
    issue_date = fields.Date()
    expiry_date = fields.Date(required=True)
    attachment_file = fields.Binary(string="Evidence File")
    attachment_filename = fields.Char(string="Filename")
    tag_ids = fields.Many2many("bbbbee.document.tag", string="Tags")


class BbbbeeCertificateBulkUploadWizard(models.TransientModel):
    _name = "bbbbee.certificate.bulk.upload.wizard"
    _table = "bbbbee_cert_bulk_upload_wizard"
    _description = "Bulk Upload Supplier Evidence"

    company_id = fields.Many2one("res.company", default=lambda self: self.env.company, required=True)
    profile_id = fields.Many2one("bbbbee.supplier.profile", required=True)
    line_ids = fields.One2many("bbbbee.certificate.bulk.upload.wizard.line", "wizard_id", string="Documents")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["company_id"] = self.env.company.id
        return super().create(vals_list)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_id = self.env.context.get("active_id")
        active_model = self.env.context.get("active_model")
        if active_model == "bbbbee.supplier.profile" and active_id:
            res["profile_id"] = active_id
        return res

    def action_create_documents(self):
        self.ensure_one()
        certificate_model = self.env["bbbbee.supplier.certificate"]
        for line in self.line_ids:
            certificate = certificate_model.create(
                {
                    "profile_id": self.profile_id.id,
                    "certificate_type": line.certificate_type,
                    "certificate_number": line.certificate_number,
                    "issue_date": line.issue_date,
                    "expiry_date": line.expiry_date,
                    "attachment_file": line.attachment_file,
                    "attachment_filename": line.attachment_filename,
                }
            )
            if line.tag_ids:
                certificate.tag_ids = [(6, 0, line.tag_ids.ids)]
        return {
            "type": "ir.actions.act_window",
            "res_model": "bbbbee.supplier.profile",
            "res_id": self.profile_id.id,
            "view_mode": "form",
            "target": "current",
        }
