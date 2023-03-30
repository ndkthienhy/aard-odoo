from math import floor, modf
from odoo import fields, api, models, _
from datetime import date,datetime,timedelta, time, tzinfo
from ast import literal_eval
from odoo import tools
from dateutil.relativedelta import relativedelta
from odoo.tools.float_utils import float_round
from pytz import timezone, utc
import babel

class HrLunch(models.Model):   
    _name = "aard.hr.lunch"
    _description = "Aardwolf Hr Lunch"
    
    name = fields.Char('Name', compute='_generate_name', store=True)
    employee_id = fields.Many2one('hr.employee', string="Employee")
    date = fields.Date('Date')
    total_working_hours = fields.Float('Total Working Hours', related='attendance_id.valid_worked_hours')
    total_overtime_hours = fields.Float('Total Overtime Hours', related='attendance_id.overtime_id.overtime_hours')
    total_meal = fields.Integer('Subtotal Meal', compute='_compute_total_meal', readonly=True, store=True)
    lunch_rule_id = fields.Many2one('aard.hr.lunch.rule', related='attendance_id.resource_calendar_id.lunch_rule_id', string='Lunch Rule', auto_join=True)
    lunch_overtime_rule_id = fields. Many2one('aard.hr.lunch.rule', compute='_compute_lunch_overtime_rule_id', string='Lunch Overtime Rule', auto_join=True)
    attendance_id = fields.Many2one('hr.attendance', string='Attendance', auto_join=True, ondelete='cascade')
    company_id = fields.Many2one('res.company', string='Company', compute='_compute_company_id', default=lambda self: self.env.user.company_id)
    
    @api.depends('employee_id', 'date')
    def _generate_name(self):
        for record in self:
            if record.employee_id and record.date:
                record.name = _('Lunch of %s for %s') % (record.employee_id.name, record.date)

    # @api.depends('attendance_id.valid_worked_hours')
    # def _compute_total_wk(self):
    #     for rec in self:
    #         att = rec.attendance_id
    #         if att.valid_worked_hours:
    #             rec.total_working_hours = att.valid_worked_hours

    # @api.depends('attendance_id.resource_calendar_id')
    # def _compute_lunch_rule_id(self):
    #     for rec in self:
    #         att = rec.attendance_id

    #         if att:
    #             calendar = att.resource_calendar_id
    #             if calendar:
    #                 rec.lunch_rule_id = calendar.lunch_rule_id.id

    @api.depends('attendance_id.resource_calendar_id')
    def _compute_lunch_overtime_rule_id(self):
        for rec in self:
            att = rec.attendance_id

            if att:
                calendar = att.resource_calendar_id
                if calendar:
                    dw = rec.date.weekday()
                    if dw == 6:
                        rec.lunch_overtime_rule_id = calendar.sunday_overtime_rule_id.lunch_rule_id.id
                    else:
                        rec.lunch_overtime_rule_id = calendar.overtime_rule_id.lunch_rule_id.id

    # @api.depends('attendance_id')
    # def _compute_total_ot(self):
    #     for rec in self:
    #         att = rec.attendance_id
    #         if att:
    #             overtime = self.env['aard.hr.overtime'].search([
    #                 ('employee_id', '=', rec.employee_id.id),
    #                 ('ot_date', '=', rec.date)
    #             ])

    #             if len(overtime) == 1:
    #                 rec.total_overtime_hours = overtime.overtime_hours

    @api.depends('total_working_hours', 'total_overtime_hours')
    def _compute_total_meal(self): 
         for record in self:
            
            if (record.lunch_rule_id or record.lunch_overtime_rule_id) and (record.total_working_hours > 0 or record.total_overtime_hours > 0):
                number_meal = 0
                number_ot_meal = 0

                if record.total_working_hours and record.lunch_rule_id.minimum_total_hours:
                    number_meal = floor(record.total_working_hours/record.lunch_rule_id.minimum_total_hours)

                if record.total_overtime_hours and record.lunch_overtime_rule_id.minimum_total_hours:
                    number_ot_meal = floor(record.total_overtime_hours/record.lunch_overtime_rule_id.minimum_total_hours)

                total_meal = number_meal * record.lunch_rule_id.number_meal + number_ot_meal * record.lunch_overtime_rule_id.number_meal
                record.total_meal = total_meal
        
    @api.depends('attendance_id.company_id')
    def _compute_company_id(self):
        for rec in self:
            if rec.attendance_id.company_id:
                rec.company_id = rec.attendance_id.company_id

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

class HrLunchGenerate(models.Model):   
    _name = "aard.hr.lunch.generate"
    _description = "Generate Lunch"
    
    employee_id = fields.Many2one('hr.employee', string="Employee")
    contract_id = fields.Many2one('hr.contract', string="Contract", compute='_compute_get_contract_id', store=True, readonly=True)
    date_start = fields.Date('Date Start')
    date_end = fields.Date('Date End')

    @api.constrains('date_start', 'date_end')
    def _constrains_date(self):
        self.ensure_one()
        if self.date_start and self.date_end and self.date_start > self.date_end:
            raise models.ValidationError('"Date End" cannot be earlier than "Date Start".')

    def _check_overlap(self):
        self.ensure_one()
        ovt_plan = self.env['aard.hr.lunch.generate'].search([
            ('employee_id', '=', self.employee_id.id), 
            ('date_start', '<=', self.date_start), 
            ('date_end', '>=', self.date_start)
            ])
        
        if ovt_plan:
            raise models.ValidationError(_('Lunch of %s has created from %s to %s.') % (ovt_plan.employee_id.name, ovt_plan.date_start, ovt_plan.date_end))
    
    @api.depends('employee_id')
    def _compute_get_contract_id(self):
        for item in self:
            if item.employee_id.contract_id:
                item.contract_id = item.employee_id.contract_id.id
            elif item.employee_id and not item.employee_id.contract_id:
                raise models.ValidationError(_('%s have been not any contract. Please generate one') % (item.employee_id.name))
            
    
    @api.multi
    def action_generate_lunch(self):
        self.ensure_one()
        if self.contract_id and self.date_start and self.date_end:
            start = datetime.combine(self.date_start, time.min)
            end = datetime.combine(self.date_end, time.max)
            hrlunch = self.env['aard.hr.lunch']
            hrattendance = self.env['hr.attendance'].search([
                ('employee_id', '=', self.employee_id.id),
                ('check_in', '>=', start),
                ('check_in', '<=', end)
                ])
            if hrattendance:
                for record in hrattendance:
                    calendar = record.resource_calendar_id
                    empid = record.employee_id.id

                    tz = timezone(calendar.tz)
                    punching_dt = record.check_in.astimezone(tz)
                    punching_date = punching_dt.date()

                    lunch = {
                        'employee_id': empid,
                        'date': punching_date,
                        'attendance_id': record.id,
                    }
                    record.write({'lunch_created': True})
                    hrlunch.create(lunch)

class HrLunchAttendance(models.Model):
    _inherit = "hr.attendance"

    lunch_id = fields.One2many('aard.hr.lunch', 'attendance_id', string='Lunch')
    lunch_created = fields.Boolean(string="Lunch Created", default=False)
    total_meal = fields.Integer('Total Meal', related="lunch_id.total_meal", store=True, readonly=True)

    @api.multi
    def _generate_lunch(self):
        hrlunch = self.env['aard.hr.lunch']

        att = self.env['hr.attendance'].search([('lunch_created', '=', False)])
        for rec in att:
            calendar = rec.resource_calendar_id
            empid = rec.employee_id.id

            # punching_dt = rec.check_in
            if calendar.tz:
                tz = timezone(calendar.tz)
                punching_dt = rec.check_in.astimezone(tz)
            else:
                punching_dt = fields.Datetime.context_timestamp(self, fields.Datetime.from_string(rec.check_in))

            punching_date = punching_dt.date()

            lunch = {
                'employee_id': empid,
                'date': punching_date,
                'attendance_id': rec.id,
            }
            hrlunch.create(lunch)
            rec.lunch_created = True

    @api.multi
    def create(self, values):
        sup = super(HrLunchAttendance, self).create(values)
        self._generate_lunch()

        return sup