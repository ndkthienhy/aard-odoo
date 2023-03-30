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

class HrLunchRule(models.Model):   
    _name = "aard.hr.lunch.rule"
    _description = "Lunch rule to apply automatic for attendance"

    name = fields.Char(string='Name', required=True)
    minimum_total_hours = fields.Float(string='Minimum Total Hours', required=True)
    number_meal = fields.Integer(string='Number of meal per total hour', default=1, required=True)

    @api.constrains('minimum_total_hours')
    def _constrains_minimum_total_hours(self):
        self.ensure_one()
        if self.minimum_total_hours <= 0:
            raise models.ValidationError('Total hours must be over 0.')
    
    @api.constrains('number_meal')
    def _constrains_number_meal(self):
        self.ensure_one()
        if self.number_meal <= 0:
            raise models.ValidationError('Total hours must be over 0.')
    
    
class HrLunchShift(models.Model):
    _inherit = 'resource.calendar'
    
    lunch_rule_id = fields.Many2one('aard.hr.lunch.rule', string='Lunch Rule', auto_join=True)

    @api.constrains('lunch_rule_id')
    def _constrains_check_overlap_hour(self):
        self.ensure_one()
        if self.hours_per_day < self.lunch_rule_id.minimum_total_hours:
            raise models.ValidationError('"Average hour per day" of "Working Hour" cannot earlier than "Total hours" of "Lunch Rule" .')
    
    
class HrLunchOvertime(models.Model):
    _inherit = 'aard.hr.overtime.rule'
    
    lunch_rule_id = fields.Many2one('aard.hr.lunch.rule', string='Lunch Rule', auto_join=True)

    @api.constrains('lunch_rule_id')
    def _constrains_check_overlap_hour(self):
        self.ensure_one()
        if self.hour_start and self.hour_end:
            totalhours = self.hour_end - self.hour_start
            if totalhours < self.lunch_rule_id.minimum_total_hours:
                raise models.ValidationError('"Total hours" of "Overtime Rule" cannot earlier than "Total hours" of "Lunch Rule" .')