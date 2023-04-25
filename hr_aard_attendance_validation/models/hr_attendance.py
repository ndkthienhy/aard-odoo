# -*- coding: utf-8 -*-
#

from odoo import models, fields, api, exceptions, _
from datetime import datetime, time, timedelta
from math import floor, ceil
from pytz import timezone, utc


class HrAttendance(models.Model):
    _inherit = "hr.attendance"
    _order = "employee_id, check_in desc"

    valid_check_in = fields.Datetime(string='Valid Check-in',compute='_compute_valid_check_in', readonly=True, store=True)
    valid_check_out = fields.Datetime(string='Valid Check-out',compute='_compute_valid_check_out', readonly=True, store=True)
    late_attendance_hours = fields.Float(string='Late', compute='_compute_late_attendance_hours', default=0, readonly=True, store=True)
    early_leave_hours  = fields.Float(string='Early', compute='_compute_early_leave_hours', default=0, readonly=True, store=True)
    valid_worked_hours  = fields.Float(string='Att Hours', compute='_compute_valid_worked_hours', default=0, readonly=True, store=True)
    attendance_days  = fields.Float(string='Attendance Days', compute='_compute_attendance_days', default=0, readonly=True, store=True)
    resource_calendar_id = fields.Many2one('resource.calendar', compute='_compute_shift', string='Working Schedule', auto_join=True, store=True)

    def _get_config_late_checkin(self, att):
        return self.env['ir.config_parameter'].sudo().get_param('attendance.allow_late_checkin') and self.env.user.company_id.minute_late_checkin or att.company_id.minute_late_checkin or 0
    def _get_config_early_checkout(self, att):
        return self.env['ir.config_parameter'].sudo().get_param('attendance.allow_early_checkout') and self.env.user.company_id.minute_early_checkout or att.company_id.minute_early_checkout or 0

    @api.multi
    def _get_resource_calendar(self, employ_id, date_day):
        contracts = self.env['hr.contract'].sudo(self.env.user.id).search([('employee_id', '=', employ_id), ('date_start', '<=', date_day)])
        if contracts:
            for contract in contracts:
                if contract.shift_schedule:
                    for shift_schedule in contract.shift_schedule:
                        if shift_schedule.start_date <= date_day and shift_schedule.end_date >= date_day:
                            return shift_schedule.hr_shift

    @api.depends('check_in', 'employee_id.resource_calendar_id', 'employee_id.contract_id.resource_calendar_id', 'employee_id.contract_id.shift_schedule.hr_shift')
    def _compute_shift(self):
        for attendance in self:
            if attendance.check_in:

                # Timezone have get by order: contract, employee.
                tz = attendance.employee_id.tz
                tzinfo = timezone(tz)
                checkin = attendance.check_in.astimezone(tzinfo)
                checkin_date = checkin.date()
            # elif attendance.check_out:
                # checkin_date = attendance.check_out.date()

            if checkin_date:
                # contracts = self.env['hr.contract'].sudo(self.env.user.id).search([('employee_id', '=', attendance.employee_id.id)])
                rc = False
                contract = attendance.employee_id.contract_id
                if contract:
                    if contract.shift_schedule:
                        for shift_schedule in contract.shift_schedule:
                            if shift_schedule.start_date <= checkin_date and shift_schedule.end_date >= checkin_date:
                                rc = shift_schedule.hr_shift.id
                    else:
                        rc = contract.resource_calendar_id
                else:
                    rc = attendance.employee_id.resource_calendar_id
                
                attendance.resource_calendar_id = rc

    @api.multi
    def _get_valid_attendace(self, attendance, punching_type = 'checkin'):
        attendance.ensure_one()

        # Timezone have get by order: calendar, contract, employee.
        tz = attendance.resource_calendar_id.tz or attendance.employee_id.tz
        tzinfo = timezone(tz)
        
        punching_datetime = attendance.check_in
        if punching_type == 'checkout':
            punching_datetime = attendance.check_out

        dt_tz = punching_datetime.astimezone(tzinfo)
        punching_date = dt_tz.date()
        punching_time = dt_tz.time()
        checkin_dayofweek = punching_date.weekday()

        total_hours = float(punching_time.hour) + punching_time.minute / 60 + punching_time.second / 3600
        ck_time = False

        # get utc offset from timezone of checkin
        calendar = attendance.resource_calendar_id
        tz_td = timedelta(hours=0)
        if calendar.tz:
            tz = timezone(calendar.tz)
            if dt_tz.tzinfo != None:
                tz_td = punching_datetime.astimezone(tz).utcoffset()

        if attendance.resource_calendar_id:
            calendar_attendance = self.env['resource.calendar.attendance'].sudo(self.env.user.id).search([('calendar_id', '=', attendance.resource_calendar_id.id), ('dayofweek', '=', checkin_dayofweek)])
            if calendar_attendance:
                if punching_type == 'checkin':
                    for ca in calendar_attendance:
                        hf = ca.hour_from
                        ht = ca.hour_to
                        if(total_hours <= ht):
                            h = floor(hf)
                            m = floor((hf - float(h)) * 60)
                            ck_time = time(hour=h, minute = m)
                            break
                elif punching_type == 'checkout':
                    for ca in calendar_attendance:
                        hf = ca.hour_from
                        ht = ca.hour_to
                        if(total_hours > hf):
                            h = floor(ht)
                            m = floor((ht - float(h)) * 60)
                            ck_time = time(hour=h, minute = m)

        if ck_time != False:
            dt_valid = datetime.combine(punching_date, ck_time)
            return dt_valid - tz_td
                   
    def _get_valid_attendance_allowed(self, attendance, ischeckin = True):
        allowed_minute = 0
        dt_attendance = attendance.valid_check_in
        if ischeckin and self._get_config_late_checkin(attendance):
            allowed_minute =  int(self._get_config_late_checkin(attendance))
        elif not ischeckin and self._get_config_early_checkout(attendance):
            allowed_minute = -int(self._get_config_early_checkout(attendance))
            dt_attendance = attendance.valid_check_out

        return dt_attendance + timedelta(minutes=allowed_minute)
    
    @api.depends('check_in', 'resource_calendar_id')
    def _compute_valid_check_in(self):
        for attendance in self:
            if attendance.check_in:
                attendance.valid_check_in = self._get_valid_attendace(attendance)


    @api.depends('check_out', 'resource_calendar_id')
    def _compute_valid_check_out(self):
        for attendance in self:
            if attendance.check_out:
                attendance.valid_check_out = self._get_valid_attendace(attendance, 'checkout')

    def _apply_block_minute(self, late_second):
        block_minute = self.env['ir.config_parameter'].sudo().get_param('attendance.block_minute') and self.env.user.company_id.block_minute or 0
        if block_minute > 0:
            block_second = block_minute * 60
            remain = late_second % block_second
            
            if remain > 60:
                return (late_second - remain) + block_second
        
        return late_second

    @api.depends('check_in', 'valid_check_in', 'resource_calendar_id')
    def _compute_late_attendance_hours(self):
        for attendance in self:
            if attendance.check_in and attendance.valid_check_in:
                # include minutes of late coming
                valid_checkin = self._get_valid_attendance_allowed(attendance)
                if attendance.check_in.replace(second=0) > valid_checkin:
                    # late = real checkin - schedule working checkin
                    late_attendance = attendance.check_in - attendance.valid_check_in
                    late_attendance_hours = self._apply_block_minute(late_attendance.total_seconds()) / 3600
                    attendance.late_attendance_hours = late_attendance_hours

    @api.depends('check_out', 'valid_check_out', 'resource_calendar_id')
    def _compute_early_leave_hours(self):
        for attendance in self:
            if attendance.check_out and attendance.valid_check_out:
                # include minutes of early
                valid_ck_out = self._get_valid_attendance_allowed(attendance, False)
                if attendance.check_out < valid_ck_out:
                    # minute = schedule working checkout - real checkout
                    early_leave = attendance.valid_check_out - attendance.check_out
                    early_leave_hours = self._apply_block_minute(early_leave.total_seconds()) / 3600
                    attendance.early_leave_hours = early_leave_hours

    @api.depends('valid_check_in', 'valid_check_out', 'resource_calendar_id')
    def _compute_valid_worked_hours(self):
        
        for attendance in self:
            # ck_in = attendance.check_in
            break_hours = 0
            if attendance.valid_check_out and attendance.valid_check_in and attendance.valid_check_out > attendance.valid_check_in:
                # Calculate total hour of break lunch time
                td_total = attendance.valid_check_out - attendance.valid_check_in
                total_worked_hours = td_total.total_seconds() / 3600
                avr_worked_hour = attendance.resource_calendar_id.hours_per_day
                if total_worked_hours > avr_worked_hour:
                    break_hours = total_worked_hours - avr_worked_hour
                    
                total_deducted_hours = break_hours + attendance.late_attendance_hours + attendance.early_leave_hours
                if total_deducted_hours < total_worked_hours:
                    attendance.valid_worked_hours = total_worked_hours - total_deducted_hours

    @api.depends('valid_worked_hours', 'resource_calendar_id')
    def _compute_attendance_days(self):
        
        for attendance in self:
            if attendance.valid_worked_hours > 0 and attendance.resource_calendar_id:
                # Calculate total hour of break lunch time
                attendance.attendance_days = float(attendance.valid_worked_hours/attendance.resource_calendar_id.hours_per_day)