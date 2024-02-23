# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Sitaram Solutions (<https://sitaramsolutions.in/>).
#
#    For Module Support : info@sitaramsolutions.in  or Skype : contact.hiren1188
#
##############################################################################

from odoo import api, models, _


class product_product(models.Model):
    _inherit = "product.product"

    @api.multi
    def name_get(self):
        product_list = []
        pricelist = self.env['product.pricelist'].browse(self._context.get('pricelist'))
        if pricelist:
            for record in pricelist.item_ids:
                if record.applied_on == '0_product_variant':
                    product_list.append(record.product_id.id)
                elif record.applied_on == '1_product':
                    product_list.extend(record.product_tmpl_id.product_variant_ids.ids)
                elif record.applied_on == '2_product_category':
                    product_id = self.env['product.product'].search([('categ_id','=',record.categ_id.id)])
                    product_list.extend(product_id.ids)
                else:
                    product_id = self.env['product.product'].search([])
                    product_list.extend(product_id.ids)
        if product_list:
            self = self.browse(product_list)
        result = super(product_product, self).name_get()
        return result