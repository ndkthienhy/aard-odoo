{
    'name': 'Sale Invoice Custom',
    'summary': "Change templace invoice",
    'description': """Modify Template Invoice""",
    'author': "Duy Khanh Nguyen",
    'category': 'Sales',
    'version': '12.0.1',
    'depends': ['sale'],
    'data': [
        'views/res_config_settings_views.xml',
        'views/sale_views.xml',
        'report/custom_invoice_report.xml'
    ],
    'demo': [],
    'license': 'LGPL-3',
}