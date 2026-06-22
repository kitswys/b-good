from odoo import fields, models


class BbbbeeEvidenceItem(models.Model):
    _name = "bbbbee.evidence.item"
    _description = "B-BBEE Evidence Item"

    pack_id = fields.Many2one("bbbbee.evidence.pack", required=True, ondelete="cascade")
    name = fields.Char(required=True)
    item_type = fields.Selection(
        [
            ("certificate", "Supplier Certificate"),
            ("spend_schedule", "Spend Schedule"),
            ("missing_evidence", "Missing Evidence"),
            ("exception_register", "Exception Register"),
            ("audit_log", "Audit Log"),
            ("summary", "Summary"),
        ],
        required=True,
    )
    attachment_id = fields.Many2one("ir.attachment")
    tag_ids = fields.Many2many("bbbbee.document.tag", string="Tags")
    note = fields.Text()
