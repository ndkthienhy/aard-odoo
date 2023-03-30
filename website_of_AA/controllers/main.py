from odoo import http
from odoo.addons.website.controllers.main import QueryURL, Website

  
class ProductCategoryDisplay2(Website):
    @http.route('/', type='http', auth="public", website=True)
    def homepageshow_aa(self,**kw):
        keep = QueryURL('/')
        Category = http.request.env['product.public.category']
        categs = Category.search([('parent_id', '=', False)])
        values = {
            'categories': categs,
            'keep': keep,
        }
        return http.request.render("website.homepage",values)