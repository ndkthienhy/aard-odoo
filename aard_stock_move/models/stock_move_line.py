from collections import Counter

from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    note = fields.Text(related='picking_id.note', store=True, readonly=False)