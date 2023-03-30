# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2018-BroadTech IT Solutions (<http://www.broadtech-innovations.com/>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

from odoo import fields, api, models, _

class HrOvertimeRule(models.Model):   
    _name = "aard.hr.overtime.rule"
    _description = "Aardwolf Overtime Rule"

    name = fields.Char(string='Overtime Name', required=True)
    hour_start = fields.Float(string='Time Start', required=True)
    hour_end = fields.Float(string='Time End', required=True)
    minimum_ot_minute = fields.Integer(string='Minimum Overtime Minute', default=0)
    block_minutes = fields.Integer(string='Block minute', default=0)
    maximum_leave_day = fields.Integer(string='Maximum Leave Day Of Week', default=0)
    resour_calendar_id = fields.One2many('resource.calendar', 'overtime_rule_id', string='Shift')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)


    @api.constrains('hour_end')
    def _check_hour_end(self):
        self.ensure_one()
        if self.hour_start > self.hour_end:
            raise models.ValidationError('"Hour end" time cannot be earlier than "Hour start" time.')
    
    @api.onchange('minimum_ot_minute')
    def _onchange_minimum_ot(self):
        self.ensure_one()
        self.minimum_ot_minute = abs(self.minimum_ot_minute)

    @api.onchange('block_minutes')
    def _onchange_minute_block(self):
        self.ensure_one()
        self.block_minutes = abs(self.block_minutes)

    @api.onchange('maximum_leave_day')
    def _onchange_leave_day(self):
        self.ensure_one()
        self.maximum_leave_day = abs(self.maximum_leave_day)
    
    
class HrOvertimeShift(models.Model):
    _inherit = 'resource.calendar'
    
    overtime_rule_id = fields.Many2one('aard.hr.overtime.rule', string='Overtime Rule', auto_join=True)
    sunday_overtime_rule_id = fields.Many2one('aard.hr.overtime.rule', string='Sunday OT Rule', auto_join=True)

    @api.constrains('overtime_rule_id')
    def _constrains_check_overlap_hour(self):
        self.ensure_one()

        ot_rule = self.env['aard.hr.overtime.rule'].search([('id', '=', self.overtime_rule_id.id)])
        if len(ot_rule) == 1:
            for attendance in self.attendance_ids:
                if attendance.hour_to < ot_rule.hour_start < attendance.hour_from or attendance.hour_to < ot_rule.hour_end < attendance.hour_from:
                    raise models.ValidationError('"Hour end" or "Hour start" must exclude period of shift.')

# class OvertimeAttendance(models.Model):
#     _inherit = "hr.attendance"

#     overtime_rule_id = fields.Many2one('aard.hr.overtime.rule', string='Overtime Rule', compute='_compute_get_overtime_rule', store=True)

#     @api.depends('resource_calendar_id')
#     def _compute_get_overtime_rule(self):
#         for att in self:
#             if att.resource_calendar_id:
#                 ovt_rule = self.env['aard.hr.overtime.rule'].search([('resour_calendar_id', '=', att.resour_calendar_id.id)])
#                 if ovt_rule:
#                     att.overtime_rule_id = ovt_rule.id