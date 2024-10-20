import json

from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale


class ShopRating(WebsiteSale):

    @http.route()
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        res = super(ShopRating, self).shop(page=page,
                                           category=category,
                                           search=search, ppg=ppg,
                                           **post)
        rating = request.env['rating.rating']
        products = res.qcontext['products']
        rating_templates = {}
        for product in products:
            ratings = rating.search([('message_id', 'in',
                                      product.website_message_ids.ids)])
            rating_product = product.rating_get_stats([('website_published', '=', True)])
            rating_templates[product.id] = rating_product
            res.qcontext['rating_product'] = rating_templates
        return res

    @http.route()
    def cart(self, **post):
        res = super(ShopRating, self).cart(**post)

        values_cart = self.checkout_values(**post)
        res.qcontext.update({
            'values_cart': values_cart,
        })
        return res

    @http.route('/update/cart-qty', type="json", auth="public", website=True)
    def cart_qty(self, product_id, line_id, add_qty=None, set_qty=0, **post):
        order = request.website.sale_get_order(force_create=1)
        if order:
            from_currency = order.company_id.currency_id
            to_currency = order.pricelist_id.currency_id
            compute_currency = lambda price: from_currency.compute(price,
                                                                   to_currency)
        else:
            compute_currency = lambda price: price

        values = {
            'website_sale_order': order,
            'compute_currency': compute_currency,
            'suggested_products': [],
        }

        if order:
            _order = order
            if not request.env.context.get('pricelist'):
                _order = order.with_context(pricelist=order.pricelist_id.id)
            values['suggested_products'] = _order._cart_accessories()

        if order.state != 'draft':
            request.website.sale_reset()

        order._cart_update(product_id=product_id, line_id=line_id,
                           add_qty=add_qty, set_qty=set_qty)
        if not order.cart_quantity:
            request.website.sale_reset()
        values.update({
            'values_cart': self.checkout_values(**post),
        })
        return request.env['ir.ui.view'].render_template(
            "website_sale.cart_popover", values)
