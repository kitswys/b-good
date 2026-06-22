from odoo import models


class BbbbeeOdooAccountingAdapter(models.AbstractModel):
    _name = "bbbbee.odoo.accounting.adapter"
    _description = "Odoo Accounting Adapter"

    def get_posted_vendor_moves(self, date_start, date_end, company):
        return self.env["account.move"].search(
            [
                ("company_id", "=", company.id),
                ("state", "=", "posted"),
                ("move_type", "in", ("in_invoice", "in_refund")),
                ("invoice_date", ">=", date_start),
                ("invoice_date", "<=", date_end),
            ]
        )
