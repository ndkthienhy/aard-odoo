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
from odoo.exceptions import Warning
from odoo import models, fields, api, _


class HrEmployeeContract(models.Model):
    _inherit = 'hr.contract'

    shift_schedule = fields.One2many('hr.shift.schedule', 'rel_hr_schedule', string="Shift Schedule")
    working_hours = fields.Many2one('resource.calendar', string='Working Schedule')
    department_id = fields.Many2one('hr.department', string='Department')
    attendance = fields.Boolean(string='Based on Attendance', default=False)


class HrSchedule(models.Model):
    _name = 'hr.shift.schedule'

    start_date = fields.Date(string="Date From", required=True)
    end_date = fields.Date(string="Date To", required=True)
    rel_hr_schedule = fields.Many2one('hr.contract')
    hr_shift = fields.Many2one('resource.calendar', string="Shift", required=True, auto_join=True)
    company_id = fields.Many2one('res.company', string='Company')

    @api.multi
    def write(self, vals):
        self._check_overlap(vals)
        return super(HrSchedule, self).write(vals)

    @api.model
    def create(self, vals):
        self._check_overlap(vals)
        return super(HrSchedule, self).create(vals)

    def _check_overlap(self, vals):
        if vals.get('start_date', False) and vals.get('end_date', False):
            val_start_date = fields.Date.from_string(vals.get('start_date'))
            val_end_date = fields.Date.from_string(vals.get('end_date'))
            # shifts = self.env['hr.shift.schedule'].search([('rel_hr_schedule', '=', vals.get('rel_hr_schedule'))])
            # for each in shifts:
            #     if each != shifts[-1]:
            #         if each.end_date >= val_start_date or each.start_date >= val_start_date:
            #             raise Warning(_('The dates may not overlap with one another.'))
            if val_start_date > val_end_date:
                raise Warning(_('Start date should be less than end date.'))

