# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Aardwolf HR Employees Rule',
    'version': '12.0.0.1.1.1',
    'category': 'Human Resources',
    'author': "Nguyen Duy Khanh",
    'company': 'Aardwolf Industries LLC',
    'sequence': 751,
    'summary': 'Centralize employee security group',
    'description': "",
    'website': 'https://www.toolrange.com.vn/',
    'depends': [
        'hr', 'hr_contract'
    ],
    'data': [
        'security/hr_employee_security.xml',
        'security/ir.model.access.csv',

        'views/hr_contract_views.xml'
    ],
}
