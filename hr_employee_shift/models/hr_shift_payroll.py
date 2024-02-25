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
from datetime import timedelta
from odoo import models, fields, api, _, tools
from datetime import datetime, time
import datetime
import math
from pytz import utc
from odoo.tools.float_utils import float_round
from collections import namedtuple


class HrPayroll(models.Model):
    _inherit = 'hr.payslip'

    ## create 10-02-2023 by Nguyen Duy Khanh
    # @api.model
    # def get_worked_day_lines(self, contracts, date_from, date_to):
    #     """
    #     @param contract: Browse record of contracts
    #     @return: returns a list of dict containing the input that should be applied for the given contract between date_from and date_to
    #     """
    #     res = []
    #     # fill only if the contract as a working schedule linked
    #     for contract in contracts.filtered(lambda contract: contract.shift_schedule.start_date > date_from and contract.shift_schedule.end_date < date_to):
    #         day_from = datetime.combine(fields.Date.from_string(date_from), time.min)
    #         day_to = datetime.combine(fields.Date.from_string(date_to), time.max)

    #         #Get Calendar from shift schedule
    #         for shift in contract.shift_schedule:
    #             # compute leave days
    #             leaves = {}
    #             # calendar = contract.resource_calendar_id
    #             calendar = shift.hr_shift
    #             tz = timezone(calendar.tz)
    #             day_leave_intervals = contract.employee_id.list_leaves(day_from, day_to, calendar=contract.resource_calendar_id)
    #             for day, hours, leave in day_leave_intervals:
    #                 holiday = leave.holiday_id
    #                 current_leave_struct = leaves.setdefault(holiday.holiday_status_id, {
    #                     'name': holiday.holiday_status_id.name or _('Global Leaves'),
    #                     'sequence': 5,
    #                     'code': holiday.holiday_status_id.name or 'GLOBAL',
    #                     'number_of_days': 0.0,
    #                     'number_of_hours': 0.0,
    #                     'contract_id': contract.id,
    #                 })
    #                 current_leave_struct['number_of_hours'] += hours
    #                 work_hours = calendar.get_work_hours_count(
    #                     tz.localize(datetime.combine(day, time.min)),
    #                     tz.localize(datetime.combine(day, time.max)),
    #                     compute_leaves=False,
    #                 )
    #                 if work_hours:
    #                     current_leave_struct['number_of_days'] += hours / work_hours

    #             # compute worked days
    #             work_data = contract.employee_id.get_work_days_data(day_from, day_to, calendar=contract.resource_calendar_id)
    #             attendances = {
    #                 'name': _("Normal Working Days paid at 100%"),
    #                 'sequence': 1,
    #                 'code': 'WORK100',
    #                 'number_of_days': work_data['days'],
    #                 'number_of_hours': work_data['hours'],
    #                 'contract_id': contract.id,
    #             }

    #             res.append(attendances)
    #             res.extend(leaves.values())
    #     return res
    ## End create 27-03-2023 by Nguyen Duy Khanh

    # @api.model
    # def get_worked_day_lines(self, contract_ids, date_from, date_to):
    #     """
    #     @param contract_ids: list of contract id
    #     @return: returns a list of dict containing the input that should be applied for the given contract between date_from and date_to
    #     """
    #     def was_on_leave_interval(employee_id, date_from, date_to):
    #         date_from = fields.Datetime.to_string(date_from)
    #         date_to = fields.Datetime.to_string(date_to)
    #         return self.env['hr.leave'].search([
    #             ('state', '=', 'validate'),
    #             ('employee_id', '=', employee_id),
    #             # ('type', '=', 'remove'),
    #             ('date_from', '<=', date_from),
    #             ('date_to', '>=', date_to)
    #         ], limit=1)

    #     res = []
    #     # fill only if the contract as a working schedule linked
    #     uom_day = self.env.ref('product.product_uom_day', raise_if_not_found=False)
    #     for contract in contract_ids:
    #         uom_hour = self.env.ref('product.product_uom_hour', raise_if_not_found=False)
    #         interval_data = []
    #         holidays = self.env['hr.leave']
    #         attendances = {
    #             'name': _("Normal Working Days paid at 100%"),
    #             'sequence': 1,
    #             'code': 'WORK100',
    #             'number_of_days': 0.0,
    #             'number_of_hours': 0.0,
    #             'contract_id': contract.id,
    #         }
    #         leaves = {}

    #         # Gather all intervals and holidays
    #         for days in contract.shift_schedule:
    #             start_date = datetime.datetime.strptime(str(days.start_date), tools.DEFAULT_SERVER_DATE_FORMAT)
    #             end_date = datetime.datetime.strptime(str(days.end_date), tools.DEFAULT_SERVER_DATE_FORMAT)
    #             nb_of_days = (days.end_date - days.start_date).days + 1
    #             for day in range(0, nb_of_days):
    #                 working_intervals_on_day = days.hr_shift._get_day_work_intervals(
    #                     start_date + timedelta(days=day))
    #                 for interval in working_intervals_on_day:
    #                     interval_data.append(
    #                         (interval, was_on_leave_interval(contract.employee_id.id, interval[0], interval[1])))

    #         # Extract information from previous data. A working interval is considered:
    #         # - as a leave if a hr.holiday completely covers the period
    #         # - as a working period instead
    #         for interval, holiday in interval_data:
    #             holidays |= holiday
    #             hours = (interval[1] - interval[0]).total_seconds() / 3600.0
    #             if holiday:
    #                 # if he was on leave, fill the leaves dict
    #                 if holiday.holiday_status_id.name in leaves:
    #                     leaves[holiday.holiday_status_id.name]['number_of_hours'] += hours
    #                 else:
    #                     leaves[holiday.holiday_status_id.name] = {
    #                         'name': holiday.holiday_status_id.name,
    #                         'sequence': 5,
    #                         'code': holiday.holiday_status_id.name,
    #                         'number_of_days': 0.0,
    #                         'number_of_hours': hours,
    #                         'contract_id': contract.id,
    #                     }
    #             else:
    #                 # add the input vals to tmp (increment if existing)
    #                 attendances['number_of_hours'] += hours
    #         # Clean-up the results
    #         leaves = [value for key, value in leaves.items()]
    #         for data in [attendances] + leaves:
    #             data['number_of_days'] = uom_hour._compute_quantity(data['number_of_hours'], uom_day) \
    #                 if uom_day and uom_hour \
    #                 else data['number_of_hours'] / 8.0
    #             res.append(data)
    #     return res


class Calendar(models.Model):
    _inherit = 'resource.calendar'
    _interval_obj = namedtuple('Interval', ('start_datetime', 'end_datetime', 'data'))

    ## create 10-02-2023 by Nguyen Duy Khanh
    crossday = fields.Boolean(string='Crossday', default=False, compute='_compute_cross_day', store=True)

    @api.depends('attendance_ids')
    def _compute_cross_day(self):
        for rec in self:
            attendances = rec.attendance_ids.filtered(lambda attendance: not attendance.date_from and not attendance.date_to)
            
            for attendance in attendances:
                if attendance.hour_from == 0:
                    rec.crossday = True
                    break
    ## End create 10-02-2023 by Nguyen Duy Khanh

    def string_to_datetime(self, value):
        """ Convert the given string value to a datetime in UTC. """
        return utc.localize(fields.Datetime.from_string(value))

    def float_to_time(self, hours):
        """ Convert a number of hours into a time object. """
        if hours == 24.0:
            return time.max
        fractional, integral = math.modf(hours)
        return time(int(integral), int(float_round(60 * fractional, precision_digits=0)), 0)

    def _interval_new(self, start_datetime, end_datetime, kw=None):
        kw = kw if kw is not None else dict()
        kw.setdefault('attendances', self.env['resource.calendar.attendance'])
        kw.setdefault('leaves', self.env['resource.calendar.leaves'])
        return self._interval_obj(start_datetime, end_datetime, kw)

    @api.multi
    def _get_day_work_intervals(self, day_date, start_time=None, end_time=None, compute_leaves=False,
                                resource_id=None):
        self.ensure_one()

        if not start_time:
            start_time = datetime.time.min
        if not end_time:
            end_time = datetime.time.max

        working_intervals = [att_interval for att_interval in
                             self._iter_day_attendance_intervals(day_date, start_time, end_time)]

        # filter according to leaves
        if compute_leaves:
            leaves = self._get_leave_intervals(
                resource_id=resource_id,
                start_datetime=datetime.datetime.combine(day_date, start_time),
                end_datetime=datetime.datetime.combine(day_date, end_time))
            working_intervals = [
                sub_interval
                for interval in working_intervals
                for sub_interval in self._leave_intervals(interval, leaves)]

        # adapt tz
        return [self._interval_new(
            self.string_to_datetime(interval[0]),
            self.string_to_datetime(interval[1]),
            interval[2]) for interval in working_intervals]

    @api.multi
    def _get_day_attendances(self, day_date, start_time, end_time):
        """ Given a day date, return matching attendances. Those can be limited
        by starting and ending time objects. """
        self.ensure_one()
        weekday = day_date.weekday()
        attendances = self.env['resource.calendar.attendance']

        for attendance in self.attendance_ids.filtered(
            lambda att:
                int(att.dayofweek) == weekday and
                not (att.date_from and fields.Date.from_string(att.date_from) > day_date) and
                not (att.date_to and fields.Date.from_string(att.date_to) < day_date)):
            if start_time and self.float_to_time(attendance.hour_to) < start_time:
                continue
            if end_time and self.float_to_time(attendance.hour_from) > end_time:
                continue
            attendances |= attendance
        return attendances

    def _iter_day_attendance_intervals(self, day_date, start_time, end_time):
        """ Get an iterator of all interval of current day attendances. """
        for calendar_working_day in self._get_day_attendances(day_date, start_time, end_time):
            from_time = self.float_to_time(calendar_working_day.hour_from)
            to_time = self.float_to_time(calendar_working_day.hour_to)

            dt_f = datetime.datetime.combine(day_date, max(from_time, start_time))
            dt_t = datetime.datetime.combine(day_date, min(to_time, end_time))

            yield self._interval_new(dt_f, dt_t, {'attendances': calendar_working_day})



