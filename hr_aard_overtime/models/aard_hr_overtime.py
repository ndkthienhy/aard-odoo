from math import floor, modf
from odoo import fields, api, models, _
from odoo.exceptions import UserError, ValidationError
from odoo import tools
from odoo.tools.float_utils import float_round
from datetime import date,datetime,timedelta, time, tzinfo
from ast import literal_eval
from dateutil.relativedelta import relativedelta
import babel


class HrOvertimeAttendance(models.Model):
    _inherit = "hr.attendance"

    overtime_id = fields.One2many('aard.hr.overtime', 'attendance_id', string='Overtime')
    overtime_hours = fields.Float('OT Hours (1.5)', compute='_compute_ot_normal', store=True, readonly=True)
    sunday_overtime_hours = fields.Float('OT Hours (2.0)', compute='_compute_ot_sunday', store=True, readonly=True)
    
    @api.depends('overtime_id.overtime_hours')
    def _compute_ot_normal(self):
        for record in self:
            if record.overtime_id.ot_date != False:
                wd = record.overtime_id.ot_date.weekday()
                if wd != 6:
                    record.overtime_hours = record.overtime_id.overtime_hours

    @api.depends('overtime_id.overtime_hours')
    def _compute_ot_sunday(self):
        for record in self:
            if record.overtime_id.ot_date != False:
                wd = record.overtime_id.ot_date.weekday()
                if wd == 6:
                    record.sunday_overtime_hours = record.overtime_id.overtime_hours

    @api.onchange('check_in', 'check_out')
    def prevent_modify(self):
        self.ensure_one()
        if self.overtime_id and self.overtime_hours:
            raise models.ValidationError(_("The %d date of attendance have 1 OT record have created. You can not modify it.") % (self.overtime_id.ot_date))

class HrOvertime(models.Model):   
    _name = "aard.hr.overtime"
    _description = "Aardwolf Hr Overtime"
    _order = 'id desc'
    
    name = fields.Char('Name', compute='_generate_name', store=True)
    employee_id = fields.Many2one('hr.employee', string="Employee")
    ot_date = fields.Date('Date')
    time_start = fields.Float('Time Start')
    time_end = fields.Float('Time End', default=lambda self: fields.Date.to_string((datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()))
    overtime_hours = fields.Float('Overtime Hours', compute='_compute_overtime_hours', store=True, readonly=True)
    attendance_id = fields.Many2one('hr.attendance', string='Attendance', auto_join=True)
    overtime_rule_id = fields.Many2one('aard.hr.overtime.rule', string='Overtime Rule', compute='_compute_get_ot_rule')
    overtime_plan_id = fields.Many2one('aard.hr.overtime.plan', string='Overtime Plan', ondelete='cascade')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)

    @api.constrains('time_start', 'time_end')
    def _constrains_time(self):
         for ovt in self:
            if ovt.time_start and ovt.time_end and ovt.time_end < ovt.time_start:
                raise models.ValidationError(_('"Time End" of %s date cannot be earlier than "Time Start".') % (ovt.ot_date))
            
    @api.constrains('time_start', 'time_end', 'overtime_rule_id')
    def _constrains_overlap_time(self):
        for ovt in self:
            if ovt.overtime_rule_id:
                if (ovt.time_start and ovt.time_end and ovt.time_end > ovt.time_start):
                    ovt_rule = self.env['aard.hr.overtime.rule'].search([('id', '=', ovt.overtime_rule_id.id)])

                    if len(ovt_rule) == 1:
                        if ovt.time_start < ovt.overtime_rule_id.hour_start:
                            raise models.ValidationError(_("Time start of %s date must between %s and %s") % (ovt.ot_date, self.env['resource.calendar'].float_to_time(ovt_rule.hour_start), self.env['resource.calendar'].float_to_time(ovt_rule.hour_end)))
                        if ovt.time_end > ovt.overtime_rule_id.hour_end:
                            raise models.ValidationError(_("Time end of %s date must between %s and %s") % (ovt.ot_date, self.env['resource.calendar'].float_to_time(ovt_rule.hour_start), self.env['resource.calendar'].float_to_time(ovt_rule.hour_end)))
            else:
                raise models.ValidationError(_('employee %s has been not overtime rule. Maybe their contract is expired, please check again.') % (ovt.employee_id.name))
            
    @api.constrains('time_start', 'time_end', 'employee_id', 'ot_date')
    def _constrains_overlap(self):
        for rec in self:
            if rec.employee_id and rec.ot_date and rec.time_start:
                ovt = self.env['aard.hr.overtime'].search([
                    ('employee_id', '=', rec.employee_id.id),
                    ('ot_date', '=', rec.ot_date),
                    ('time_start', '<=', rec.time_start),
                    ('time_end', '>=', rec.time_start)
                    ])
                if len(ovt) >= 2:
                    raise models.ValidationError(_('OT of %s on %s date has been check-in from %s to %s hours')
                                                  % (rec.employee_id.name, rec.ot_date, self.env['resource.calendar'].float_to_time(rec.time_start), self.env['resource.calendar'].float_to_time(rec.time_end)))
            
    @api.depends('employee_id', 'ot_date')
    def _generate_name(self):
        for record in self:
            if record.employee_id and record.ot_date:
                record.name = _('OT of %s for %s') % (record.employee_id.name, record.ot_date)

    @api.depends('time_start', 'time_end', 'overtime_rule_id')
    def _compute_overtime_hours(self):
         for ovt in self:
            if ovt.time_start and ovt.time_end and ovt.time_end > ovt.time_start:
                overtime_hours = ovt.time_end - ovt.time_start
                ovt.overtime_hours = overtime_hours

    def _search_att_ot_hours(self):
        if self.time_start and self.time_end and self.time_end > self.time_start:
            return self.time_end - self.time_start
        return 0

    @api.depends('employee_id', 'ot_date', 'attendance_id.resource_calendar_id')
    def _compute_get_ot_rule(self):
         for ovt in self:
            dow = ovt.ot_date.weekday()
            if ovt.attendance_id:
                if dow == 6:
                    ovt.overtime_rule_id = ovt.attendance_id.resource_calendar_id.sunday_overtime_rule_id.id
                else:
                    ovt.overtime_rule_id = ovt.attendance_id.resource_calendar_id.overtime_rule_id.id

            elif ovt.employee_id and ovt.ot_date:
                shifts = self.env['hr.shift.schedule'].search([('rel_hr_schedule', '=', ovt.employee_id.contract_id.id), ('start_date', '<=', ovt.ot_date), ('end_date', '>=', ovt.ot_date)], order='start_date desc', limit=1)

                if len(shifts) == 1:
                    if dow == 6:
                        ovt.overtime_rule_id = shifts.hr_shift.sunday_overtime_rule_id.id
                    else:
                        ovt.overtime_rule_id = shifts.hr_shift.overtime_rule_id.id

    @api.onchange('attendance_id.check_out')
    def _onchange_checkout(self):
        if self.attendance_id.check_out:
            ovt_rule = self.attendance_id.resource_calendar_id.overtime_rule_id
            if ovt_rule:
                att_ckout = fields.Datetime.context_timestamp(self, fields.Datetime.from_string(self.attendance_id.check_out))
                att_time = att_ckout.time()

                time_start = self.time_start
                time_end = self.time_end

                att_time_hours = float(att_time.hour) + float(att_time.minute/60) + float(att_time.second/3600)
                
                if att_time_hours > self.time_start:
                    time_end = att_time_hours
                    if time_end > time_start:
                        ovt_hours = time_end - time_start
                        if (ovt_rule.minimum_ot_minute > 0 and ovt_hours*60 > ovt_rule.minimum_ot_minute) or ovt_rule.minimum_ot_minute == 0:
                            self.time_end = att_time_hours

        
    @api.multi
    def action_view_attendance(self):
        attendances = self.mapped('attendance_id')
        action = self.env.ref('hr_attendance.hr_attendance_action').read()[0]
        if len(attendances) > 1:
            action['domain'] = [('id', 'in', attendances.ids)]
        elif len(attendances) == 1:
            action['views'] = [(self.env.ref('hr_attendance.hr_attendance_view_form').id, 'form')]
            action['res_id'] = self.attendance_id.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

class HrOvertimePlan(models.Model):   
    _name = "aard.hr.overtime.plan"
    _description = "Aardwolf Hr Overtime Plan"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    def _default_employee(self):
        return self.env.context.get('default_employee_id') or self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
    
    name = fields.Char('Name')
    employee_id = fields.Many2one('hr.employee', string="Employee", default=_default_employee)
    contract_id = fields.Many2one('hr.contract', string="Contract", related="employee_id.contract_id", store=True, readonly=True)
    date_start = fields.Date('Date Start', 
                             default=lambda self: fields.Date.to_string(date.today().replace(day=1)))
    date_end = fields.Date('Date End',
                           default=lambda self: fields.Date.to_string((datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()))
    total_hours = fields.Float('Total OT Hours', compute='_compute_total_hours', defaulf=0.00, store=True)
    notes = fields.Text(string='Notes')
    overtime_plan_lines = fields.One2many('aard.hr.overtime', 'overtime_plan_id', 
                                          string="Overtime Lines",
                                          states={'cancel': [('readonly', True)], 'validate': [('readonly', True)]}, 
                                          copy=True, auto_join=True, store=True, readonly=False)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Waiting Approval'), 
        ('refuse', 'Refused'), 
        ('validate', 'Approved'), 
        ('cancel', 'Cancelled')],
        default='draft', copy=False, track_visibility='onchange',
        help="The status is set to 'To Submit', when a leave request is created." +
        "\nThe status is 'To Approve', when leave request is confirmed by user." +
        "\nThe status is 'Refused', when leave request is refused by manager." +
        "\nThe status is 'Approved', when leave request is approved by manager.")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)

    @api.constrains('date_start', 'date_end')
    def _constrains_date(self):
        self.ensure_one()
        if self.date_start and self.date_end and self.date_start > self.date_end:
            raise models.ValidationError('"Date End" cannot be earlier than "Date Start".')
        
    @api.constrains('total_hours', 'state')
    def constrains_total_hours(self):
        self.ensure_one()
        if int(self.total_hours) == 0 and self.state == "validate":
            raise models.ValidationError(_('%s must have at least 1 overtime record.') % (self.name))
        
    @api.onchange('employee_id', 'date_start')
    def _onchange_employee(self):
        self.ensure_one()
        if self.employee_id and self.date_start:
            empl = self.employee_id
            ttyme = datetime.combine(self.date_start, time.min)
            locale = self.env.context.get('lang') or 'en_US'
            self.name = _('OT of %s for %s') % (empl.name, tools.ustr(babel.dates.format_date(date=ttyme, format='MMMM-y', locale=locale)))

    @api.onchange('overtime_plan_lines')
    def _onchange_ot_plan_lines(self):
        self.ensure_one()
        if self.overtime_plan_lines:
            ot_date = []
            for ot_line in self.overtime_plan_lines:
                ot_line.employee_id = self.employee_id.id
                if ot_line.ot_date:
                    ot_date.append(ot_line.ot_date)
            
            if ot_date:
                date_min = min(ot_date)
                date_max = max(ot_date)

                # if (self.date_start and date_min < self.date_start):
                self.date_start = date_min
                # if (self.date_end and date_max < self.date_end):
                self.date_end = date_max
    
    # @api.depends('employee_id')
    # def _compute_get_contract_id(self):
    #     for item in self:
    #         if item.employee_id.contract_id:
    #             item.contract_id = item.employee_id.contract_id.id
    #         elif item.employee_id and not item.employee_id.contract_id:
    #             raise models.ValidationError(_('%s have been not any contract. Please generate one') % (item.employee_id.name))

    @api.depends('overtime_plan_lines')
    def _compute_total_hours(self):
        for rec in self:
            if rec.overtime_plan_lines:
                total_hours = 0
                for ovt in rec.overtime_plan_lines:
                    total_hours += ovt.overtime_hours
                
                if total_hours > 0:
                    rec.total_hours = total_hours
    
    # @api.depends('contract_id', 'date_start', 'date_end')
    def _compute_calculate_overtime_attendance(self):
        if self.contract_id and self.date_start and self.date_end and self.date_end > self.date_start:
            #combine date and time with timezone of self
            dt_from = datetime.combine(self.date_start, time.min)
            dt_to = datetime.combine(self.date_end, time.max)

            attendances = self.env['hr.attendance'].search([('employee_id', '=', self.employee_id.id), ('check_in', '>=', dt_from), ('check_in', '<=', dt_to), ('check_out', '!=', False), ('resource_calendar_id', '!=', False), ('company_id', '=', self.employee_id.company_id.id)])
            if attendances:
                plan_lines = []
                for att in  attendances:
                    att_ckout = fields.Datetime.context_timestamp(self, fields.Datetime.from_string(att.check_out))
                    att_ckin = fields.Datetime.context_timestamp(self, fields.Datetime.from_string(att.check_in))
                    ckout_att_date = att_ckout.date()
                    ckout_att_time = att_ckout.time()
                    ckin_att_date = att_ckin.date()
                    ckin_att_time = att_ckin.time()

                    dw = ckin_att_date.weekday()
                    ovt_rule = False
                    calendar_attendance = False


                    if dw == 6 and att.resource_calendar_id.sunday_overtime_rule_id:
                        ovt_rule = att.resource_calendar_id.sunday_overtime_rule_id
                    elif dw != 6 and att.resource_calendar_id.overtime_rule_id:
                        ovt_rule = att.resource_calendar_id.overtime_rule_id

                    if ovt_rule != False:
                        worked_hours_include_break = 0
                        if att.valid_check_out and att.valid_check_in and dw != 6:
                            att_valid_ckout = fields.Datetime.context_timestamp(self, fields.Datetime.from_string(att.valid_check_out))
                            att_valid_ckin = fields.Datetime.context_timestamp(self, fields.Datetime.from_string(att.valid_check_in))
                            dt_worked_hours = att_valid_ckout - att_valid_ckin
                            worked_hours_include_break = dt_worked_hours.total_seconds()/3600
                            # raise models.ValidationError(_('OT of %s.') % (worked_hours_include_break))

                        ot_time_start = ovt_rule.hour_start
                        ot_time_end = ovt_rule.hour_end

                        # add 15 minute early checkin, late checkout
                        att_time_from = float(ckin_att_time.hour) + float((ckin_att_time.minute)/60) + float(ckin_att_time.second/3600)
                        att_time_to = float(ckout_att_time.hour) + float((ckout_att_time.minute)/60) + float(ckout_att_time.second/3600)
                        
                        # Creating a OT record must to statisfy following:
                        # ++ check-in must between 'time start' and 'time end' or,
                        # ++ check-out must between 'time start' and 'time end' and,
                        # ++ actual worked hour must more than total of worked hour (include break hours) and minimum allow overtime
                        if (ot_time_start < att_time_from + float(15/60) < ot_time_end or ot_time_start < att_time_to - float(15/60) < ot_time_end) and ((worked_hours_include_break > 0 and att.worked_hours > (worked_hours_include_break + float(ovt_rule.minimum_ot_minute/60)) or dw == 6)):
                            #OT before working hours
                            if ot_time_start < att_time_from + float(15/60) < ot_time_end and dw != 6:
                                att_time_from = max(att_time_from,ot_time_start)
                                att_time_to = ot_time_end

                            # OT after working hours
                            if ot_time_start < att_time_to - float(15/60) < ot_time_end and dw != 6:
                                att_time_from = ot_time_start
                                att_time_to = min(att_time_to,ot_time_end)

                            # OT on sunday
                            if dw == 6:
                                att_time_from = max(att_time_from,ot_time_start)
                                att_time_to = min(att_time_to,ot_time_end)

                            if att_time_to > att_time_from:
                                ovt_hours = att_time_to - att_time_from
                                if (ovt_rule.minimum_ot_minute > 0 and ovt_hours*60 > ovt_rule.minimum_ot_minute) or ovt_rule.minimum_ot_minute == 0:
                                    ovt_item = {
                                        'employee_id': att.employee_id.id,
                                        'ot_date': ckin_att_date,
                                        'time_start': att_time_from,
                                        'time_end': att_time_to,
                                        'attendance_id': att,
                                        'company_id': self.company_id.id
                                    }
                                    plan_lines.append(ovt_item)
                self.overtime_plan_lines = plan_lines
                    
    @api.multi
    def action_submit(self):
        return self.write({'state':'confirm'})
        
    @api.multi
    def action_cancel(self):
        return self.write({'state':'cancel'})
        
    @api.multi
    def action_approve(self):
        self._compute_calculate_overtime_attendance()
        return self.write({'state':'validate'})
    
    @api.multi
    def action_refuse(self):
        return self.write({'state':'refuse'})

    @api.multi
    def write(self, vals):
        self.ensure_one()
        if self.state not in ('draft', 'cancel', 'confirm'):
            raise UserError(_('You can not modify a confirmed request OT.'))
        if vals.get('state') == "validate":
            self._check_overlap(vals)
        return super(HrOvertimePlan, self).write(vals)

    @api.model
    def create(self, vals):
        self._check_overlap(vals)
        return super(HrOvertimePlan, self).create(vals)
    
    # restrick delete if record have approved
    @api.multi
    def unlink(self):
        self.ensure_one()
        if self.state not in ('draft', 'cancel', 'confirm'):
            raise UserError(_('You can not delete a confirmed request OT.'))
        return super(HrOvertimePlan, self).unlink()
    
    def _check_overlap(self, vals):
        ovt_plan = self.search([('employee_id', '=', vals.get('employee_id')), "|", ('date_start', '<=', vals.get('date_start')), ('date_end', '>=', vals.get('date_start')), ('date_start', '<=', vals.get('date_end')), ('date_end', '>=', vals.get('date_end'))], limit=1)
        if len(ovt_plan) == 1:
            raise models.ValidationError(_('OT of %s has created from %s to %s.') % (ovt_plan.employee_id.name, ovt_plan.date_start, ovt_plan.date_end))

class HrShiftOvertime(models.Model):
    _inherit = 'hr.shift.schedule'

    def has_overtime(self, emp_id, start_date, end_date):

        overtimes = self.env['aard.hr.overtime'].search([('employee_id', '=', emp_id),('ot_date', '>=', start_date), ('ot_date', '<=', end_date)])

        if overtimes:
            return True
        return False

    @api.multi
    def write(self, vals):
        #check overtime old date if existed
        for rec in self:
            if rec.has_overtime(rec.rel_hr_schedule.employee_id.id, rec.start_date, rec.end_date):
                raise models.ValidationError(_('A Overtime from %s to %s is approved. You can not modify') % (rec.start_date, rec.end_date))
        #check overtime new date if existed
            if rec.has_overtime(rec.rel_hr_schedule.employee_id.id, vals.get('start_date'), vals.get('end_date')):
                raise models.ValidationError(_('A Overtime from %s to %s is approved. You can not modify') % (vals.get('start_date'), vals.get('end_date')))

        return super(HrShiftOvertime, self).write(vals)
    @api.multi
    def create(self, vals):
        if isinstance(vals, list):
            for val in vals:
                contract_id = val.get('rel_hr_schedule', False)
                if contract_id:
                    contract = self.env['hr.contract'].search([('id', '=', contract_id)])
                    if contract:
                        emp = contract.employee_id
                        if self.has_overtime(emp.id, val.get('start_date'), val.get('end_date')):
                            raise models.ValidationError(_('A Overtime of %s from %s to %s is approved. You can not create') % (emp.name, val.get('start_date'), val.get('end_date')))
        return super(HrShiftOvertime, self).create(vals)
    @api.multi
    def unlink(self):
        if self.has_overtime(self.rel_hr_schedule.employee_id.id, self.start_date, self.end_date):
            raise models.ValidationError(_('A Overtime from %s to %s is approved. You can not delete') % (self.start_date, self.end_date))
        return super(HrShiftOvertime, self).unlink()