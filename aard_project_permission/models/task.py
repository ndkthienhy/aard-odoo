# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class ProjectTask(models.Model):
    _inherit = ['project.task']

    def _get_followers(self, project):
        current_user_id = self.env.uid
        user = self.env['res.users'].browse(current_user_id)
        user_follow = []

        #get all users have been following particular project
        if project:
            followers = project.message_partner_ids
            if followers:
                for partner in followers:
                    user_follow.append(partner.user_ids.id)
        
        #filter list of user base on role
        if current_user_id in user_follow and (user.has_group('project.group_project_manager') or (user.has_group('aard_project_permission.group_project_owner_manager') and project.user_id.id == current_user_id)):
            return user_follow
        elif current_user_id in user_follow:
            return current_user_id
        else:
            return False
        
    def _get_domain_followers(self):

        if self.env.context.get('default_project_id'):
            user_follow = []
            project = self.env['project.project'].search([('id', '=', self.env.context.get('default_project_id'))])
            if project:
                user_follow = self._get_followers(project)
            if user_follow:
                return [('id', 'child_of', user_follow)]
        return [('id', 'child_of', 0)]

    user_id = fields.Many2one('res.users',
        string='Assigned to',
        default=lambda self: self.env.uid,
        index=True, track_visibility='always',
        domain=_get_domain_followers)
        
    @api.onchange('project_id')
    def _onchange_project(self):
        super(ProjectTask, self)._onchange_project()

        user_follow = []
        if self.project_id:
            user_follow = self._get_followers(self.project_id)

        return {'domain': {'user_id': [('id', 'child_of', user_follow)]}}