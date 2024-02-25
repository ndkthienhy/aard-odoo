# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64
import logging

from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError, AccessError
from odoo.modules.module import get_module_resource

class PrivateInfoEmployee(models.Model):
    _inherit = "hr.employee"

    # resource and user
    # required on the resource, make sure required="True" set in the view
    employee_code = fields.Char('Employee Code', groups="hr.group_hr_user")
    id_issue_date = fields.Date(string="Date of issue", groups="hr.group_hr_user")
    #id_expiry_date = fields.Date('Expiry Date', groups="hr.group_hr_user")
    place_of_issue = fields.Char('Place of issue', groups="hr.group_hr_user")
    other_dependant = fields.Integer(string='Grantee', groups="hr.group_hr_user")
    personal_tax_id = fields.Char('Personal Tax ID', groups="hr.group_hr_user")
    level_edu = fields.Char('Level of education', groups="hr.group_hr_user")
    permanent_address = fields.Char('Permanent Address', groups="hr.group_hr_user")