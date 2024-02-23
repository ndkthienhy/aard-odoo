# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Sitaram Solutions (<https://sitaramsolutions.in/>).
#
#    For Module Support : info@sitaramsolutions.in  or Skype : contact.hiren1188
#
##############################################################################

{
    'name': "Product Based On Pricelist",
    'version': "12.0.0.3",
    'category': 'Sale',
    "license": "OPL-1",
    'summary': "This module allows you to select only those product which is assigned to the pricelist.",
    'description': """
         This module allows you to select only those product which is assigned to the pricelist.
         sale pricelist
         product restricted with pricelist
         product select based on pricelist 
    """,
    'author': "Sitaram",
    'depends': ['base','sale_management','product'],
    'data': [
        ],
    'website': "https://www.sitaramsolutions.in",
    'application': True,
    'installable': True,
    'auto_install': False,
    'live_test_url': 'https://youtu.be/lZOpCcY734E',
    "images": ['static/description/banner.png'],
}
