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
# Maintainer: Nguyen Duy Khanh
# Company: Aardwolf Industrial LLC
# Date start: 12/30/2022
###################################################################################
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, Warning
from datetime import date, timedelta

class HrGenerateShift(models.Model):
    _name = 'hr.shift.generate'

    hr_department = fields.Many2one('hr.department', string="Department")
    start_date = fields.Date(string="Start Date", required=True, default = fields.Date.today)
    end_date = fields.Date(string="End Date", required=True)
    company_id = fields.Many2one('res.company', string='Company')
    #Added by Nguyen Duy khanh
    employee_id = fields.Many2one('hr.employee', string='Employee', required = True)
    contract_id = fields.Many2one('hr.contract', string = 'Contract', required = True, related="employee_id.contract_id")
    resource_calendar_id = fields.Many2one('resource.calendar', string='Working Schedule', required = True)
    rotating_shift = fields.Boolean(string='Rotating Shift', default=False)
    rotating_resource_calendar = fields.Many2one('resource.calendar', string='Rotating Schedule')
    rotating_employee_id = fields.Many2one('hr.employee', string='Rotating With')
    rotating_contract = fields.Many2one('hr.contract', string = 'Rotating Contract')

    @api.constrains('start_date', 'end_date')
    def _constrains_date(self):
        if self.start_date > self.end_date:
            raise ValidationError(_('Start date should be less than end date.'))

    @api.constrains('rotating_resource_calendar')
    def _constrains_resource_calendar(self):
        if self.resource_calendar_id == self.rotating_resource_calendar:
            raise ValidationError(_('Rotating Work Schedule and Working Schedule are must different.'))
        
    @api.constrains('employee_id')
    def _constrains_employee_contract(self):
        if self.employee_id == self.rotating_employee_id:
            raise ValidationError(_('This employee have chosen'))
        contracts = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id)])
        if not contracts:
            raise ValidationError(_('This employee have not any contract. Create one please'))
    
    @api.constrains('rotating_shift', 'start_date', 'end_date')
    def _constrains_rotating_shift_time(self):
        if self.rotating_shift:
            td = self.end_date - self.start_date
            if td.days <= 14:
                raise ValidationError(_('Rotating shift only assign for period over 2 week'))
            
    @api.constrains('end_date')
    def _constrains_end_date(self):
        if self.contract_id.date_end and self.end_date and self.contract_id.date_end > self.end_date:
            raise ValidationError(_('End date do not exceed end date of contract'))

                    
    @api.onchange('contract_id')
    def onchange_contract(self):
        if self.contract_id:
            current_date = date.today()
            if self.contract_id.date_start and current_date < self.contract_id.date_start:
                self.start_date = self.contract_id.date_start

            if self.contract_id.date_end:
                if self.contract_id.date_end > current_date:
                    self.end_date = self.contract_id.date_end
                else:
                    self.end_date = current_date
            else:
                self.end_date = date(current_date.year , 12, 31)
        
        if self.rotating_contract:
            if self.rotating_contract.date_end and self.end_date and self.rotating_contract.date_end < self.end_date:
                self.end_date = self.rotating_contract.date_end

    @api.onchange('employee_id')
    def onchange_employee(self):
        if self.employee_id:
            self.rotating_employee_id = ''
            self.rotating_contract = ''
            self.contract_id = ''

    
    @api.onchange('rotating_contract')
    def onchange_rotating_contract(self):
        if self.rotating_contract:
            if self.rotating_contract.date_end and self.end_date and self.rotating_contract.date_end < self.end_date:
                self.end_date = self.rotating_contract.date_end

    @api.multi
    def _assign_shift_schedule(self, contract_id, start_date, end_date, shift_id):
        shift_ids = [(0, 0, {
                'hr_shift': shift_id,
                'start_date': start_date,
                'end_date': end_date
            })]
        if contract_id:
            contract_id.shift_schedule = shift_ids

    @api.multi
    # Firstday is Sunday. With Monday is 0, Sunday is 6, and use date.weekday()
    def _get_remain_day(self,current_date, firstday = 0):
        wd = current_date.weekday()
        # If first day of week isn't monday, end day of week is previous day
        # get day of week by weekday()
        lastday = firstday - 1
        if lastday == -1:
            lastday = 6

        remain_wday = lastday - wd
        if remain_wday < 0:
            remain_wday += 7
            
        return remain_wday

 
    @api.multi
    def _rotating_shift(self, contract_id, start_date, end_date, shift_id, rotating_shift = 0):
        if rotating_shift == 0:
            self._assign_shift_schedule(contract_id, start_date, end_date, shift_id)
        else:
            # First day is Sunday
            remain_wdays = self._get_remain_day(start_date, 6)
            tmp_start_date = start_date
            tmp_end_date = tmp_start_date + timedelta(days=remain_wdays)
            shift = 0
            while tmp_end_date < end_date:
                if rotating_shift != 0:
                    if shift == shift_id:
                        shift = rotating_shift
                    elif shift == rotating_shift:
                        shift = shift_id
                    else:
                        shift = shift_id
                else:
                    shift = shift_id
                self._assign_shift_schedule(contract_id, tmp_start_date, tmp_end_date, shift)
                tmp_start_date = tmp_end_date + timedelta(days=1)
                tmp_end_date = tmp_end_date + timedelta(days=7)
            else:
                if rotating_shift != 0:
                    if shift == shift_id:
                        shift = rotating_shift
                    elif shift == rotating_shift:
                        shift = shift_id
                else:
                    shift = shift_id
                tmp_end_date = end_date
                self._assign_shift_schedule(contract_id, tmp_start_date, tmp_end_date, shift)

    @api.multi
    def action_schedule_shift(self):
        """Create mass schedule for all departments based on the shift scheduled in corresponding employee's contract"""

        sd = self.start_date
        ed = self.end_date
        shift_id = self.resource_calendar_id.id
        rotating_shift = self.rotating_resource_calendar.id
        if self.employee_id:
            self._rotating_shift(self.contract_id, sd, ed, shift_id, rotating_shift)
        if self.rotating_employee_id:
            self._rotating_shift(self.rotating_contract, sd, ed, rotating_shift, shift_id)