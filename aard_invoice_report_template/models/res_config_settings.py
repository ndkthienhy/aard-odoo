# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    use_payment_bank_note = fields.Boolean(string="Default Bank Payment", config_parameter='sale.use_payment_bank_note')
    sale_note_bank_info = fields.Text(related="company_id.sale_note_bank_info", string="Payment Bank Information", readonly=False)