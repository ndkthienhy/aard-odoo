# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp

class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    @api.model
    def _default_note_bank(self):
        return self.env['ir.config_parameter'].sudo().get_param('sale.use_payment_bank_note') and self.env.user.company_id.sale_note_bank_info or ''

    sale_note_bank_info = fields.Text(string="Bank Information", default=_default_note_bank)
    
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    price_unit = fields.Monetary('Unit Price', required=True, digits=dp.get_precision('Product Price'), default=0.0)