from odoo import models


class IrModuleModule(models.Model):
    _inherit = "ir.module.module"

    def action_open_bbbbee_dashboard(self):
        self.ensure_one()
        return self.env.ref("bbbbee_procurement.action_bbbbee_dashboard").read()[0]
