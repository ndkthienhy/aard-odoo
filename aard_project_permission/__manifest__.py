{
    'name': "Aardwolf Project Permission",
    'summary': "",
    'description': """Set rule for Project""",
    'category': 'Project',
    'author': "Nguyen Duy Khanh",
    'company': 'Aardwolf Industries LLC',
    'website': "https://www.odoo.com/page/website-builder",
    'version': '12.0.1.0.0.1',
    'depends': ['project', 'project_team'],
    'data': [
        'security/project_security.xml',
        'security/ir.model.access.csv',
        'views/project_views.xml',
    ],
    'demo': [],
}