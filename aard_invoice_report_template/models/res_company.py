# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields

class ResCompany(models.Model):
    _inherit = "res.company"

    sale_note_bank_info = fields.Text(string="Sale Note Bank Information")