# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResPartner(models.Model):
    """ Inherits partner and adds Tasks information in the partner form """
    _inherit = 'res.partner'

    project_ids = fields.Many2many('project.project', 'project_user_followers_rel', 'message_partner_ids', 'project_id', string='Projects')
