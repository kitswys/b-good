from odoo import models


class BbbbeeSpendClassifier(models.AbstractModel):
    _name = "bbbbee.spend.classifier"
    _description = "Procurement Spend Classifier"

    def classify_move(self, move):
        if move.move_type in ("in_invoice", "in_refund") and move.state == "posted":
            return "included"
        return "review"
