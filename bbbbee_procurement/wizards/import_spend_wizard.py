from odoo import fields, models


class BbbbeeImportSpendWizard(models.TransientModel):
    _name = "bbbbee.import.spend.wizard"
    _description = "Import B-BBEE Procurement Spend"

    measurement_period_id = fields.Many2one("bbbbee.measurement.period", required=True)
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company, required=True)

    def action_import(self):
        period = self.measurement_period_id
        batch = self.env["bbbbee.spend.batch"].create(
            {
                "name": "Spend Import - %s" % period.name,
                "measurement_period_id": period.id,
                "company_id": self.company_id.id,
            }
        )
        return {
            "type": "ir.actions.act_window",
            "res_model": "bbbbee.spend.batch",
            "res_id": batch.id,
            "view_mode": "form",
        }
