# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    allow_late_checkin = fields.Integer(related='company_id.minute_late_checkin', string='Maximum Late Check-in',
                                        config_parameter='attendance.allow_late_checkin',
                                        implied_group="hr_attendance.group_hr_attendance_manager",
                                        readonly=False)
    allow_early_checkout = fields.Integer(related='company_id.minute_early_checkout', string='Maximum Early Check-out',
                                          config_parameter='attendance.allow_early_checkout',
                                          implied_group="hr_attendance.group_hr_attendance_manager",
                                          readonly=False)
    block_minutes = fields.Integer(related='company_id.block_minute', string='Block',
                                          config_parameter='attendance.block_minute',
                                          implied_group="hr_attendance.group_hr_attendance_manager",
                                          readonly=False)
