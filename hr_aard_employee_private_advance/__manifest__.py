# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Aardwolf HR Employees Private Information',
    'version': '12.0.0.1.1.1',
    'category': 'Human Resources',
    'author': "Nguyen Duy Khanh",
    'company': 'Aardwolf Industries LLC',
    'sequence': 752,
    'summary': 'Add new fields for private information',
    'description': """
        Add more fields:
        + Date of issue,
        + Date of expiry,
        + Place of issue,
        + Personal Tax ID,
        + Level of education,
        + Grantee,
        + Permanent Address
        + Religion
        Show fields to view (has been on database):
        + SIN No,  
        + SSN No
    """,
    'website': 'https://www.toolrange.com.vn/',
    'depends': [
        'hr'
    ],
    'data': [
        'views/hr_views.xml'
    ],
}
