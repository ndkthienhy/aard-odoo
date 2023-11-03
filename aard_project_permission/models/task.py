# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class ProjectTask(models.Model):
    _inherit = ['project.task']
    
    user_id = fields.Many2one('res.users',
        string='Assigned to',
        default="",
        index=True, track_visibility='always',
        domain=[('share', '=', False)])
        
    @api.onchange('project_id')
    def _onchange_project(self):
        super(ProjectTask, self)._onchange_project()
        if self.project_id:
            user_follow = []
            followers = self.project_id.message_partner_ids
            for partner in followers:
                user_follow.append(partner.user_ids.id)
            return {'domain': {'user_id': [('id', 'in', user_follow)]}}