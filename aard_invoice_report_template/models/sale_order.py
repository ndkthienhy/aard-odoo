# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    @api.model
    def _default_note_bank(self):
        return self.env['ir.config_parameter'].sudo().get_param('sale.use_payment_bank_note') and self.env.user.company_id.sale_note_bank_info or ''

    sale_note_bank_info = fields.Text(string="Bank Information", default=_default_note_bank)
    