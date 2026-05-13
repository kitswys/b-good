from odoo import models


class BbbbeeEvidenceExporter(models.AbstractModel):
    _name = "bbbbee.evidence.exporter"
    _description = "Evidence Pack Exporter"

    def export_pack(self, pack, export_format="xlsx"):
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Evidence export",
                "message": "Evidence pack export is not implemented yet.",
                "type": "warning",
            },
        }
