from odoo import fields, models


class BbbbeeDocumentTag(models.Model):
    _name = "bbbbee.document.tag"
    _description = "B-BBEE Document Tag"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(required=True, tracking=True)
    color = fields.Integer(default=0)
    active = fields.Boolean(default=True)
    usage = fields.Selection(
        [
            ("certificate", "Certificate"),
            ("evidence", "Evidence"),
            ("both", "Both"),
        ],
        default="both",
        required=True,
        tracking=True,
    )
