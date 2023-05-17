# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ResCompany(models.Model):
    _inherit = "res.company"

    minute_late_checkin = fields.Integer(string='Maximum Late Check-in')
    minute_early_checkout = fields.Integer(string='Maximum Early Check-out')
    block_minute = fields.Integer(string='Block')