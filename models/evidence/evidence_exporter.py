from odoo import models


class BbbbeeEvidenceExporter(models.AbstractModel):
    _name = "bbbbee.evidence.exporter"
    _description = "Evidence Pack Exporter"

    def export_pack(self, pack, export_format="xlsx"):
        if export_format == "pdf":
            return self.env.ref("bbbbee_procurement.action_report_bbbbee_evidence_pack").report_action(pack)
        return self.env.ref("bbbbee_procurement.action_report_bbbbee_evidence_pack").report_action(pack)
