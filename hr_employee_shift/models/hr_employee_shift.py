# -*- coding: utf-8 -*-
###################################################################################
#    A part of OpenHrms Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
#    Author: Saritha Sahadevan (<https://www.cybrosys.com>)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###################################################################################
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _
from odoo.tools.float_utils import float_round


class HrEmployeeInherited(models.Model):
    _inherit = 'hr.employee'

    resource_calendar_ids = fields.Many2one('resource.calendar', 'Working Hours')


class HrEmployeeShift(models.Model):
    _inherit = 'resource.calendar'
    _order = 'company_id, sequence'

    def _get_default_attendance_ids(self):
        return [
            (0, 0, {'name': _('Monday Morning'), 'dayofweek': '0', 'hour_from': 8, 'hour_to': 11.5}),
            (0, 0, {'name': _('Tuesday Morning'), 'dayofweek': '1', 'hour_from': 8, 'hour_to': 11.5}),
            (0, 0, {'name': _('Wednesday Morning'), 'dayofweek': '2', 'hour_from': 8, 'hour_to': 11.5}),
            (0, 0, {'name': _('Thursday Morning'), 'dayofweek': '3', 'hour_from': 8, 'hour_to': 11.5}),
            (0, 0, {'name': _('Friday Morning'), 'dayofweek': '4', 'hour_from': 8, 'hour_to': 11.5}),
            (0, 0, {'name': _('Saturday Morning'), 'dayofweek': '5', 'hour_from': 8, 'hour_to': 11.5}),
            (0, 0, {'name': _('Monday Evening'), 'dayofweek': '0', 'hour_from': 12.5, 'hour_to': 17}),
            (0, 0, {'name': _('Tuesday Evening'), 'dayofweek': '1', 'hour_from': 12.5, 'hour_to': 17}),
            (0, 0, {'name': _('Wednesday Evening'), 'dayofweek': '2', 'hour_from': 12.5, 'hour_to': 17}),
            (0, 0, {'name': _('Thursday Evening'), 'dayofweek': '3', 'hour_from': 12.5, 'hour_to': 17}),
            (0, 0, {'name': _('Friday Evening'), 'dayofweek': '4', 'hour_from': 12.5, 'hour_to': 17}),
            (0, 0, {'name': _('Saturday Evening'), 'dayofweek': '5', 'hour_from': 12.5, 'hour_to': 17}),
        ]

    color = fields.Integer(string='Color Index')
    # hr_department = fields.Many2one('hr.department', string="Department", required=True)
    sequence = fields.Integer(string="Sequence", required=True, default=1)
    attendance_ids = fields.One2many(
        'resource.calendar.attendance', 'calendar_id', 'Workingssss Time',
        copy=True, default=_get_default_attendance_ids)
    
    @api.onchange('attendance_ids')
    def _onchange_hours_per_day(self):
        attendances = self.attendance_ids.filtered(lambda attendance: not attendance.date_from and not attendance.date_to)
        hour_count = 0.0
        for attendance in attendances:
            hour_count += attendance.hour_to - attendance.hour_from
        if attendances:
            self.hours_per_day = float_round(hour_count / float(len(attendances)/2), precision_digits=0)


    # @api.constrains('sequence')
    # def validate_seq(self):
    #     if self.hr_department.id:
    #         record = self.env['resource.calendar'].search([('hr_department', '=', self.hr_department.id),
    #                                                        ('sequence', '=', self.sequence),
    #                                                        ('company_id', '=', self.company_id.id)
    #                                                        ])
    #         if len(record) > 1:
    #             raise ValidationError("One record with same sequence is already active."
    #                                   "You can't activate more than one record  at a time")