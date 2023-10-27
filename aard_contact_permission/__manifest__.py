{
    'name': "Aardwolf Contact Permission",
    'summary': "",
    'description': """Set rule for Contacts""",
    'category': 'Tools',
    'author': "Nguyen Duy Khanh",
    'company': 'Aardwolf Industries LLC',
    'website': "https://www.odoo.com/page/website-builder",
    'version': '12.0.1.0.0.1',
    'depends': ['base', 'contacts'],
    'data': [
        'security/contact_security.xml',
        'views/contact_views.xml',
    ],
    'demo': [],
}