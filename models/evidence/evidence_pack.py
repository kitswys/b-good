import base64
import io
import zipfile

from odoo import api, fields, models


class BbbbeeEvidencePack(models.Model):
    _name = "bbbbee.evidence.pack"
    _description = "B-BBEE Evidence Pack"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(required=True)
    measurement_period_id = fields.Many2one("bbbbee.measurement.period", required=True, ondelete="cascade")
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company, required=True)
    assessment_id = fields.Many2one("bbbbee.scorecard.assessment", ondelete="set null")
    item_ids = fields.One2many("bbbbee.evidence.item", "pack_id")
    generated_on = fields.Datetime(default=fields.Datetime.now)
    version = fields.Integer(default=1)
    state = fields.Selection([("draft", "Draft"), ("generated", "Generated"), ("frozen", "Frozen")], default="draft")
    xlsx_export_file = fields.Binary(copy=False)
    xlsx_export_filename = fields.Char(copy=False)
    audit_zip_file = fields.Binary(copy=False)
    audit_zip_filename = fields.Char(copy=False)

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

    def action_freeze(self):
        self.write({"state": "frozen"})

    def action_print_pdf(self):
        return self.env.ref("bbbbee_procurement.action_report_bbbbee_evidence_pack").report_action(self)

    def action_print_missing_evidence(self):
        self.ensure_one()
        lines = self.env["bbbbee.spend.line"].search(
            [
                ("batch_id.measurement_period_id", "=", self.measurement_period_id.id),
                ("evidence_status", "in", ("missing", "review_required")),
            ]
        )
        return self.env.ref("bbbbee_procurement.action_report_bbbbee_missing_evidence").report_action(lines)

    def _download_bytes(self, payload, filename, mimetype):
        self.ensure_one()
        attachment = self.env["ir.attachment"].create(
            {
                "name": filename,
                "type": "binary",
                "datas": base64.b64encode(payload),
                "mimetype": mimetype,
                "res_model": self._name,
                "res_id": self.id,
            }
        )
        return {
            "type": "ir.actions.act_url",
            "url": "/web/content/%s?download=true" % attachment.id,
            "target": "self",
        }

    def _render_report_pdf(self, xmlid):
        report = self.env.ref(xmlid)
        pdf_content, _ = report._render_qweb_pdf(self.ids)
        return pdf_content

    def _build_xlsx_bytes(self):
        self.ensure_one()
        try:
            import xlsxwriter
        except Exception as exc:  # pragma: no cover - dependency issue should surface in runtime
            raise ValueError("xlsxwriter is required to export Excel files.") from exc

        buffer = io.BytesIO()
        workbook = xlsxwriter.Workbook(buffer, {"in_memory": True})
        header = workbook.add_format({"bold": True, "bg_color": "#dbe8ff", "border": 1})
        money = workbook.add_format({"num_format": '#,##0.00'})
        percent = workbook.add_format({"num_format": '0.00'})

        lines = self.env["bbbbee.spend.line"].search([("batch_id.measurement_period_id", "=", self.measurement_period_id.id)])
        partner_ids = lines.mapped("partner_id").ids
        profiles = self.env["bbbbee.supplier.profile"].search([("partner_id", "in", partner_ids)])
        certificates = self.env["bbbbee.supplier.certificate"].search([("partner_id", "in", partner_ids)])

        summary_sheet = workbook.add_worksheet("Summary")
        summary_rows = [
            ("Pack", self.name),
            ("Measurement Period", self.measurement_period_id.name),
            ("State", self.state),
            ("Version", self.version),
            ("Supplier Profiles", len(profiles)),
            ("Certificates", len(certificates)),
            ("Spend Lines", len(lines)),
            ("Assessment", self.assessment_id.name if self.assessment_id else ""),
            ("Measured Spend", self.assessment_id.total_measured_spend if self.assessment_id else 0.0),
            ("Recognised Spend", self.assessment_id.recognised_procurement_spend if self.assessment_id else 0.0),
            ("Achieved %", self.assessment_id.achieved_percentage if self.assessment_id else 0.0),
        ]
        summary_sheet.write_row(0, 0, ["Metric", "Value"], header)
        for row, (label, value) in enumerate(summary_rows, start=1):
            summary_sheet.write(row, 0, label)
            summary_sheet.write(row, 1, value, money if isinstance(value, (int, float)) and "Spend" in label else None)
        summary_sheet.set_column(0, 0, 24)
        summary_sheet.set_column(1, 1, 30)

        profile_sheet = workbook.add_worksheet("Supplier Profiles")
        profile_headers = ["Supplier", "Level", "Recognition %", "Compliance", "Black Ownership %", "Black Women %", "Empowering"]
        profile_sheet.write_row(0, 0, profile_headers, header)
        for row, profile in enumerate(profiles, start=1):
            profile_sheet.write(row, 0, profile.partner_id.display_name)
            profile_sheet.write(row, 1, profile.bbbbee_level)
            profile_sheet.write(row, 2, profile.recognition_percentage, percent)
            profile_sheet.write(row, 3, profile.compliance_status)
            profile_sheet.write(row, 4, profile.black_ownership_percentage, percent)
            profile_sheet.write(row, 5, profile.black_women_ownership_percentage, percent)
            profile_sheet.write(row, 6, profile.empowering_supplier_status)
        profile_sheet.set_column(0, 0, 28)
        profile_sheet.set_column(1, 6, 18)

        spend_sheet = workbook.add_worksheet("Procurement Spend")
        spend_headers = ["Supplier", "Invoice Date", "Untaxed", "Included", "Recognition %", "Recognised", "Evidence Status", "Classification"]
        spend_sheet.write_row(0, 0, spend_headers, header)
        for row, line in enumerate(lines, start=1):
            spend_sheet.write(row, 0, line.partner_id.display_name)
            spend_sheet.write(row, 1, line.invoice_date and line.invoice_date.strftime("%Y-%m-%d") or "")
            spend_sheet.write(row, 2, line.untaxed_amount, money)
            spend_sheet.write(row, 3, line.included_amount, money)
            spend_sheet.write(row, 4, line.recognition_percentage, percent)
            spend_sheet.write(row, 5, line.recognised_amount, money)
            spend_sheet.write(row, 6, line.evidence_status)
            spend_sheet.write(row, 7, line.classification)
        spend_sheet.set_column(0, 0, 28)
        spend_sheet.set_column(1, 1, 14)
        spend_sheet.set_column(2, 5, 14)
        spend_sheet.set_column(6, 7, 16)

        score_sheet = workbook.add_worksheet("Scorecard")
        score_headers = ["Metric", "Value"]
        score_sheet.write_row(0, 0, score_headers, header)
        score_rows = [
            ("Target %", self.assessment_id.target_percentage if self.assessment_id else 0.0),
            ("Achieved %", self.assessment_id.achieved_percentage if self.assessment_id else 0.0),
            ("Measured Spend", self.assessment_id.total_measured_spend if self.assessment_id else 0.0),
            ("Recognised Spend", self.assessment_id.recognised_procurement_spend if self.assessment_id else 0.0),
            ("Shortfall Amount", self.assessment_id.shortfall_amount if self.assessment_id else 0.0),
            ("Actual Points", self.assessment_id.actual_points if self.assessment_id else 0.0),
        ]
        for row, (label, value) in enumerate(score_rows, start=1):
            score_sheet.write(row, 0, label)
            score_sheet.write(row, 1, value, money if "Spend" in label or "Shortfall" in label else percent)
        score_sheet.set_column(0, 0, 24)
        score_sheet.set_column(1, 1, 20)

        evidence_sheet = workbook.add_worksheet("Evidence Items")
        evidence_sheet.write_row(0, 0, ["Item", "Type", "Tags", "Note"], header)
        for row, item in enumerate(self.item_ids, start=1):
            evidence_sheet.write(row, 0, item.name)
            evidence_sheet.write(row, 1, item.item_type)
            evidence_sheet.write(row, 2, ", ".join(item.tag_ids.mapped("name")))
            evidence_sheet.write(row, 3, item.note or "")
        evidence_sheet.set_column(0, 0, 28)
        evidence_sheet.set_column(1, 2, 18)
        evidence_sheet.set_column(3, 3, 40)

        workbook.close()
        buffer.seek(0)
        return buffer.read()

    def action_export_xlsx(self):
        self.ensure_one()
        payload = self._build_xlsx_bytes()
        self.write(
            {
                "xlsx_export_file": base64.b64encode(payload),
                "xlsx_export_filename": "audit-summary-%s.xlsx" % self.measurement_period_id.name,
            }
        )
        return self._download_bytes(payload, self.xlsx_export_filename, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    def _build_audit_zip(self):
        self.ensure_one()
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("audit-summary.xlsx", self._build_xlsx_bytes())
            archive.writestr("evidence-pack-summary.pdf", self._render_report_pdf("bbbbee_procurement.action_report_bbbbee_evidence_pack"))
            archive.writestr("missing-evidence.pdf", self._render_report_pdf("bbbbee_procurement.action_report_bbbbee_missing_evidence"))
            archive.writestr("spend-schedule.pdf", self._render_report_pdf("bbbbee_procurement.action_report_bbbbee_spend_schedule"))
            for item in self.item_ids.filtered(lambda item: item.attachment_id):
                attachment_name = item.attachment_id.name or item.name or "attachment"
                archive.writestr(attachment_name, base64.b64decode(item.attachment_id.datas or b""))
        buffer.seek(0)
        return buffer.read()

    def action_export_audit_zip(self):
        self.ensure_one()
        payload = self._build_audit_zip()
        self.write(
            {
                "audit_zip_file": base64.b64encode(payload),
                "audit_zip_filename": "audit-pack-%s.zip" % self.measurement_period_id.name,
            }
        )
        return self._download_bytes(payload, self.audit_zip_filename, "application/zip")
