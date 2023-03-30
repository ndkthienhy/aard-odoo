from collections import Counter

from odoo import fields, models, api


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    note = fields.Text(related='picking_id.note', store=True, readonly=False)
    qty_available = fields.Float(related='product_id.qty_available', store=True, readonly=False, group_operator='avg')