# -*- coding: utf-8 -*-
###################################################################################
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###################################################################################
import pytz
import sys
from datetime import datetime, time, timedelta, timezone
import logging
import binascii
import os
import platform
import subprocess

from odoo import api, fields, models
from odoo import _
from odoo.exceptions import UserError, ValidationError
from math import floor, ceil
_logger = logging.getLogger(__name__)
try:
    from zk import ZK, const
except ImportError:
    _logger.error("Unable to import pyzk library. Try 'pip3 install pyzk'.")

class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    device_id = fields.Char(string='Biometric Device ID')
    check_in_device_id = fields.Many2one('zk.machine', string='Check-in Device')
    check_out_device_id = fields.Many2one('zk.machine', string='Check-out Device')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id.id)


class ZkMachine(models.Model):
    _name = 'zk.machine'
    
    name = fields.Char(string='Machine IP', required=True)
    port_no = fields.Integer(string='Port No', required=True, default="4370")
    address_id = fields.Many2one('res.partner', string='Working Address')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id.id)
    zk_timeout = fields.Integer(string='ZK Timeout', required=True, default="120")
    zk_after_date =  fields.Datetime(string='Attend Start Date', help='If provided, Attendance module will ignore records before this date.')

    @api.multi
    def device_connect(self, zkobj):
        try:
            conn =  zkobj.connect()
            return conn
        except:
            _logger.info("zk.exception.ZKNetworkError: can't reach device.")
            raise UserError("Connection To Device cannot be established.")
            return False

    # @api.multi
    # def device_connect(self, zkobj):
    #     for i in range(10):
    #         try:
    #             conn =  zkobj.connect()
    #             return conn
    #         except:
    #             _logger.info("zk.exception.ZKNetworkError: can't reach device.")
    #             conn = False
    #     return False


    @api.multi
    def try_connection(self):
        for r in self:
            machine_ip = r.name
            if platform.system() == 'Linux':
                response = os.system("ping -c 1 " + machine_ip)
                if response == 0:
                    raise UserError("Biometric Device is Up/Reachable.")
                else:
                    raise UserError("Biometric Device is Down/Unreachable.") 
            else:
                prog = subprocess.run(["ping", machine_ip], stdout=subprocess.PIPE)
                if 'unreachable' in str(prog):
                    raise UserError("Biometric Device is Down/Unreachable.")
                else:
                    raise UserError("Biometric Device is Up/Reachable.")  
    
    @api.multi
    def clear_attendance(self):
        for info in self:
            try:
                machine_ip = info.name
                zk_port = info.port_no
                timeout = info.zk_timeout
                try:
                    zk = ZK(machine_ip, port = zk_port , timeout=timeout, password=0, force_udp=False, ommit_ping=False)
                except NameError:
                    raise UserError(_("Pyzk module not Found. Please install it with 'pip3 install pyzk'."))                
                conn = self.device_connect(zk)
                if conn:
                    conn.enable_device()
                    clear_data = zk.get_attendance()
                    if clear_data:
                        #conn.clear_attendance()
                        self._cr.execute("""delete from zk_machine_attendance""")
                        conn.disconnect()
                        raise UserError(_('Attendance Records Deleted.'))
                    else:
                        raise UserError(_('Unable to clear Attendance log. Are you sure attendance log is not empty.'))
                else:
                    raise UserError(_('Unable to connect to Attendance Device. Please use Test Connection button to verify.'))
            except:
                raise ValidationError('Unable to clear Attendance log. Are you sure attendance device is connected & record is not empty.')

    def zkgetuser(self, zk):
        try:
            users = zk.get_users()
            return users
        except:
            raise UserError(_('Unable to get Users.'))

    @api.model
    def cron_download(self):
        machines = self.env['zk.machine'].search([])
        for machine in machines :
            machine.download_attendance()
   
    # create 11-01-2023 by Nguyen Duy Khanh
    @api.multi
    def get_attendance(self, employee_id, punching_time, machine_id, company_id):
        attendances = self.env['hr.attendance']
        
        dt_punching = fields.Datetime.context_timestamp(self, fields.Datetime.from_string(punching_time))
        # dt_punching = fields.Datetime.to_datetime(punching_time)
        date_punching = dt_punching.date()
        time_punching = dt_punching.time()
        
        crossday_checkout = False

        # OR if it starts before the date_from and finish after the date_end (or never finish)
        clause_3 = ['&', ('date_start', '<=', date_punching), '|', ('date_end', '=', False), ('date_end', '>=', date_punching)]
        clause_final = [('employee_id', '=', employee_id), ('state', '=', 'open')] + clause_3
        contracts = self.env['hr.contract'].search(clause_final)
        
        # contracts = self.env['hr.contract'].search([('employee_id', '=', employee_id), ('date_start', '<=', date_punching), ('date_end', '>=', date_punching)])
        
        if len(contracts) == 1:
            shift_schedule = self.env['hr.shift.schedule'].search([('rel_hr_schedule', '=', contracts.id), ('start_date', '<=', date_punching), ('end_date', '>=', date_punching)])
            if len(shift_schedule) == 1:
                crossday_checkout = shift_schedule.hr_shift.crossday
        
        att_not_chkout = attendances.search([('employee_id', '=', employee_id), ('check_out', '=', False)])

        # Nếu có đầy đủ check-in check-out thì kiểm tra bấm công trùng hay không
        if not att_not_chkout:
            #start 13/02/2023
            if crossday_checkout:
                #get previous checkin
                att_chkout = attendances.search([('employee_id', '=', employee_id)], order='check_in asc')
                if len(att_chkout) > 0:
                    latest_att = att_chkout[-1]
                    la_date_checkin = fields.Datetime.context_timestamp(self, fields.Datetime.from_string(latest_att.check_in)).date()
                    la_date_checkout = fields.Datetime.context_timestamp(self, fields.Datetime.from_string(latest_att.check_out)).date()
                    
                    if la_date_checkin == la_date_checkout and latest_att.resource_calendar_id.crossday:
                        latest_att.write({'check_out': punching_time})
                    elif la_date_checkout > la_date_checkin and date_punching == la_date_checkout:
                        dayofweek = date_punching.weekday()
                        rca = self.env['resource.calendar.attendance'].search([('calendar_id', '=', shift_schedule.hr_shift.id), ('dayofweek', '=', dayofweek)])
                        if rca:
                            for rc in rca:
                                ckout = rc.hour_to
                                h = int(floor(ckout))
                                m = int((ckout - h)*60)
                                if 0 < h < 23:
                                    h += 1
                                
                                dt_checkout_to = datetime.combine(date_punching, time(hour=h, minute=m), timezone.utc)
                                break
                        
                        if dt_checkout_to and dt_punching < dt_checkout_to:
                            latest_att.write({'check_out': punching_time})
                        else:
                            attendances.create({'employee_id': employee_id, 'check_in': punching_time, 'check_in_device_id': machine_id, 'company_id': company_id})
                    else:
                        attendances.create({'employee_id': employee_id, 'check_in': punching_time, 'check_in_device_id': machine_id, 'company_id': company_id})
                else:
                    attendances.create({'employee_id': employee_id, 'check_in': punching_time, 'check_in_device_id': machine_id, 'company_id': company_id})
            else:
                # Chuyển ca - ngày hiện tại là ca trong ngày, nhưng ngày trước đó là ca qua đêm
                prev_crossday = False
                att_chkout = attendances.search([('employee_id', '=', employee_id)], order='check_in asc')
                if len(att_chkout) > 0:
                    latest_att = att_chkout[-1]
                    prev_crossday = latest_att.resource_calendar_id.crossday

                if prev_crossday and latest_att:
                    la_date_checkin = fields.Datetime.context_timestamp(self, fields.Datetime.from_string(latest_att.check_in)).date()
                    la_date_checkout = fields.Datetime.context_timestamp(self, fields.Datetime.from_string(latest_att.check_out)).date()
                    
                    if la_date_checkin == la_date_checkout:
                        latest_att.write({'check_out': punching_time})
                    elif la_date_checkout > la_date_checkin and date_punching == la_date_checkout:
                        dayofweek = date_punching.weekday()
                        rca = self.env['resource.calendar.attendance'].search([('calendar_id', '=', latest_att.resource_calendar_id.id), ('dayofweek', '=', dayofweek)])
                        if rca:
                            for rc in rca:
                                ckout = rc.hour_to
                                h = int(floor(ckout))
                                m = int((ckout - h)*60)
                                if 0 < h < 23:
                                    h += 1
                                
                                dt_checkout_to = datetime.combine(date_punching, time(hour=h, minute=m), timezone.utc)
                                break
                        
                        if dt_checkout_to and dt_punching < dt_checkout_to:
                            latest_att.write({'check_out': punching_time})
                        elif dt_checkout_to and dt_punching > dt_checkout_to:
                            #chuyển ca từ qua đêm sang trong ngày
                            attendances.create({'employee_id': employee_id, 'check_in': latest_att.check_out, 'check_out': punching_time, 'company_id': company_id})
                # Chỉ làm ca trong ngày
                else:
                    # min_ckout_dt = datetime.combine(date_punching, time.min)
                    # max_ckout_dt = datetime.combine(date_punching, time.max)
                    # att_chkout = attendances.search([('employee_id', '=', employee_id), ('check_out', '>=', min_ckout_dt),
                    #                                     ('check_out', '<=', max_ckout_dt)])
                    # if len(att_chkout) == 1 and not crossday_checkout:
                    #     att_chkout.write({'check_out': punching_time})
                    # else:
                        attendances.create({'employee_id': employee_id, 'check_in': punching_time, 'check_in_device_id': machine_id, 'company_id': company_id})
        # Chưa có checkout
        elif len(att_not_chkout) == 1:
            latest_checkin_tz = fields.Datetime.context_timestamp(self, fields.Datetime.from_string(att_not_chkout.check_in))
            td = dt_punching - latest_checkin_tz

            if td.total_seconds() > 300:
                lc_date = latest_checkin_tz.date()

                if date_punching == lc_date:
                        att_not_chkout.write({'check_out': punching_time, 'check_out_device_id': machine_id})
                elif date_punching > lc_date:
                    # Nếu không cùng ngày thì kiểm tra xem có lịch làm việc qua ngày hay không
                    if crossday_checkout and att_not_chkout.resource_calendar_id.crossday:
                        min_ckout_dt = datetime.combine(date_punching, time.min)
                        max_ckout_dt = datetime.combine(date_punching, time.max)
                        att_chkout = attendances.search([('employee_id', '=', employee_id), ('check_out', '>=', min_ckout_dt),
                                                         ('check_out', '<=', max_ckout_dt)])
                        if len(att_chkout) == 1:
                            att_chkout.write({'check_out': punching_time})
                        else:
                            att_not_chkout.write({'check_out': punching_time, 'check_out_device_id': machine_id})
                    elif att_not_chkout.resource_calendar_id.crossday:
                        att_not_chkout.write({'check_out': punching_time, 'check_out_device_id': machine_id})
                    else:
                        att_not_chkout.write({'check_out': att_not_chkout.check_in})
                        attendances.create({'employee_id': employee_id, 'check_in': punching_time, 'check_in_device_id': machine_id, 'company_id': company_id})

    @api.multi
    def download_attendance(self):
        _logger.info("++++++++++++Cron Executed++++++++++++++++++++++")
        zk_attendance = self.env['zk.machine.attendance']
        for info in self:
            machine_ip = info.name
            zk_port = info.port_no
            timeout = info.zk_timeout
            try:
                zk = ZK(machine_ip, port = zk_port , timeout=timeout, password=0, force_udp=False, ommit_ping=False)
            except NameError:
                raise UserError(_("Pyzk module not Found. Please install it with 'pip3 install pyzk'."))
            conn = self.device_connect(zk)
            if conn:
                # conn.disable_device() #Device Cannot be used during this time.
                try:
                    attendance = conn.get_attendance()
                except:
                    attendance = False
                if attendance:
                    for each in attendance:
                        atten_time = each.timestamp
                        atten_time = datetime.strptime(atten_time.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
                        if info.zk_after_date == False:
                            tmp_zk_after_date = datetime.strptime('2000-01-01',"%Y-%m-%d")
                        else:
                            tmp_zk_after_date = datetime.strptime(info.zk_after_date.strftime('%Y-%m-%d %H:%M:%S'),'%Y-%m-%d %H:%M:%S')

                        if atten_time != False and atten_time > tmp_zk_after_date:
                            
                            get_user_id = self.env['hr.employee'].search(
                                            [('device_id', '=', each.user_id)])
                            if get_user_id:
                                local_tz = pytz.timezone(get_user_id.tz or self.env.user.partner_id.tz or 'GMT')
                                local_dt = local_tz.localize(atten_time, is_dst=False)
                                utc_dt = local_dt.astimezone(pytz.utc)
                                utc_dt = utc_dt.strftime("%Y-%m-%d %H:%M:%S")
                                atten_time = datetime.strptime(
                                    utc_dt, "%Y-%m-%d %H:%M:%S")
                                atten_time = fields.Datetime.to_string(atten_time)

                                tmp_atten_time = datetime.strptime(
                                atten_time, "%Y-%m-%d %H:%M:%S")

                                duplicate_atten_ids = zk_attendance.search(
                                    [('device_id', '=', each.user_id), ('punching_time', '=', atten_time)])
                                if duplicate_atten_ids:
                                    continue
                                else:
                                    is_create = False
                                    atten_ids = zk_attendance.search(
                                    [('device_id', '=', each.user_id)])
                                    if atten_ids:
                                        prev_atten_time = atten_ids[-1].punching_time

                                        if prev_atten_time:
                                            td1 = tmp_atten_time - prev_atten_time
                                            #distance between two punch must over 5 minute (300 seconds)
                                            if td1.total_seconds() >= 300:
                                                is_create = True
                                    else:
                                        is_create = True

                                    if is_create:
                                        zk_attendance.create({'employee_id': get_user_id.id,
                                                'device_id': each.user_id,
                                                'attendance_type': str(each.status),
                                                'punch_type': str(each.punch),
                                                'punching_time': atten_time,
                                                'address_id': info.address_id.id,
                                                'company_id': info.company_id.id})
                                        self.get_attendance(get_user_id.id, atten_time, info.id, info.company_id.id)
                    # conn.enable_device() #Enable Device Once Done.
                    conn.disconnect
                    return True
                else:
                    raise UserError(_('No attendances found in Attendance Device to Download.'))
                    # conn.enable_device() #Enable Device Once Done.
                    conn.disconnect
            else:
                raise UserError(_('Unable to connect to Attendance Device. Please use Test Connection button to verify.'))
    # @api.multi
    # End create 11-01-2023 by Nguyen Duy Khanh

    # def download_attendance(self):
    #     _logger.info("++++++++++++Cron Executed++++++++++++++++++++++")
    #     zk_attendance = self.env['zk.machine.attendance']
    #     att_obj = self.env['hr.attendance']
    #     for info in self:
    #         machine_ip = info.name
    #         zk_port = info.port_no
    #         timeout = info.zk_timeout
    #         try:
    #             zk = ZK(machine_ip, port = zk_port , timeout=timeout, password=0, force_udp=False, ommit_ping=False)
    #         except NameError:
    #             raise UserError(_("Pyzk module not Found. Please install it with 'pip3 install pyzk'."))
    #         conn = self.device_connect(zk)
    #         if conn:
    #             # conn.disable_device() #Device Cannot be used during this time.
    #             try:
    #                 user = conn.get_users()
    #             except:
    #                 user = False
    #             try:
    #                 attendance = conn.get_attendance()
    #             except:
    #                 attendance = False
    #             if attendance:
    #                 for each in attendance:
    #                     atten_time = each.timestamp
    #                     atten_time = datetime.strptime(atten_time.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
    #                     device_atten_time = atten_time
    #                     tz = atten_time.tzinfo
    #                     if info.zk_after_date == False:
    #                         tmp_zk_after_date = datetime.strptime('2000-01-01',"%Y-%m-%d")
    #                     else:
    #                         tmp_zk_after_date = datetime.strptime(info.zk_after_date.strftime('%Y-%m-%d %H:%M:%S'),'%Y-%m-%d %H:%M:%S')
    #                     if atten_time != False and atten_time > tmp_zk_after_date:
    #                         local_tz = pytz.timezone(self.env.user.partner_id.tz or 'GMT')
    #                         local_dt = local_tz.localize(atten_time, is_dst=None)
    #                         utc_dt = local_dt.astimezone(pytz.utc)
    #                         utc_dt = utc_dt.strftime("%Y-%m-%d %H:%M:%S")
    #                         atten_time = datetime.strptime(
    #                             utc_dt, "%Y-%m-%d %H:%M:%S")
    #                         tmp_utc = local_dt.astimezone(pytz.utc)
    #                         tmp_attend = tmp_utc.strftime("%m-%d-%Y %H:%M:%S")
    #                         atten_time = fields.Datetime.to_string(atten_time)
    #                         if user:
    #                             for uid in user:
    #                                 if uid.user_id == each.user_id:
    #                                     get_user_id = self.env['hr.employee'].search(
    #                                         [('device_id', '=', each.user_id)])
    #                                     if get_user_id:
    #                                         duplicate_atten_ids = zk_attendance.search(
    #                                             [('device_id', '=', each.user_id), ('punching_time', '=', atten_time)])
    #                                         if duplicate_atten_ids:
    #                                             continue
    #                                         else:
    #                                             #[16/11/2022-Khanh] update punch_type
    #                                             each.punch = 0
                                                
    #                                             tmp_att_date = datetime.strptime(utc_dt,'%Y-%m-%d %H:%M:%S')
    #                                             tmp_datetime_min = tmp_att_date - timedelta(hours=24)
    #                                             tmp_datetime_max = tmp_att_date

    #                                             tmp_zkatten = zk_attendance.search(
    #                                                 ['&', ('device_id', '=', each.user_id), ('punching_time', '>', tmp_datetime_min), ('punching_time', '<', tmp_datetime_max)])
                                                
    #                                             if len(tmp_zkatten) > 0:
    #                                                 latest_zka = False

    #                                                 #Tính lệch múi giờ
    #                                                 dt_duration = device_atten_time - tmp_att_date
    #                                                 tz_atten_time = device_atten_time

    #                                                 for zka in tmp_zkatten:
    #                                                     tz_punching_time = datetime.strptime(zka.punching_time.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S") + dt_duration
    #                                                     if tz_punching_time.day == tz_atten_time.day and tz_punching_time.month == tz_atten_time.month and tz_punching_time.year == tz_atten_time.year:
    #                                                         latest_zka = zka

    #                                                 if latest_zka != False:
    #                                                     zka_punch_type = int(latest_zka.punch_type)
    #                                                     zka_punching_time = latest_zka.punching_time

    #                                                     td = tmp_att_date - zka_punching_time
    #                                                     if td.total_seconds() > 3600:
    #                                                         if zka_punch_type == 0:
    #                                                             each.punch = 1
    #                                                     else:
    #                                                         continue

    #                                             zk_attendance.create({'employee_id': get_user_id.id,
    #                                                                 'device_id': each.user_id,
    #                                                                 'attendance_type': str(each.status),
    #                                                                 'punch_type': str(each.punch),
    #                                                                 'punching_time': atten_time,
    #                                                                 'address_id': info.address_id.id})

    #                                             att_var = att_obj.search([('employee_id', '=', get_user_id.id),
    #                                                                     ('check_out', '=', False)])
                                                
    #                                             if each.punch == 0: #check-in
    #                                                 if not att_var:
    #                                                     attend_rec_tmp = att_obj.search([('employee_id', '=', get_user_id.id),('check_out', '>', tmp_attend)])
    #                                                     if not attend_rec_tmp:
    #                                                         att_obj.create({'employee_id': get_user_id.id,
    #                                                                         'check_in': atten_time})
    #                                                 if len(att_var) == 1:
    #                                                     td_checkin = tmp_att_date - att_var.check_in
    #                                                     #thời gian giữa 2 lần bấm > 20h
    #                                                     if td_checkin.total_seconds() > 72000:
    #                                                         att_var.write({'check_out': att_var.check_in})
    #                                                         att_obj.create({'employee_id': get_user_id.id,
    #                                                                         'check_in': atten_time})

    #                                             if each.punch == 1: #check-out
    #                                                 if len(att_var) == 1:
    #                                                     att_var.write({'check_out': atten_time})
    #                                                 else:
    #                                                     att_var1 = att_obj.search([('employee_id', '=', get_user_id.id)])
    #                                                     if att_var1:
    #                                                         att_var1[-1].write({'check_out': atten_time})

    #                                     else:
    #                                         pass
    #                                 else:
    #                                     pass
    #                 # conn.enable_device() #Enable Device Once Done.
    #                 conn.disconnect
    #                 return True
    #             else:
    #                 raise UserError(_('No attendances found in Attendance Device to Download.'))
    #                 # conn.enable_device() #Enable Device Once Done.
    #                 conn.disconnect
    #         else:
    #             raise UserError(_('Unable to connect to Attendance Device. Please use Test Connection button to verify.'))

