from odoo import models, api, fields, _


class ProductPublicCategory(models.Model):
    _inherit = "product.public.category"

    def _compute_count_total_product(self):
        for record in self:
            record.products_count = self.env['product.template'].search_count(
                [('public_categ_ids', 'child_of', record.id),
                 ('website_published', '=', True)])

    products_count = fields.Integer(
        compute="_compute_count_total_product", string="Category Total Product")


class Website(models.Model):
    _inherit = 'website'

    @api.multi
    def get_categories(self):
        category_ids = self.env['product.public.category'].search(
            [('parent_id', '=', False)])
        res = {
            'categories': category_ids,
        }
        return res

    @api.multi
    def get_blogs(self):
        blog_ids = self.env['blog.post'].search(
            [('website_published', '=', True)])
        return blog_ids
