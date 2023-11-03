{
    'name': "Aardwolf Permission Advance",
    'summary': "",
    'description': """Set permission assignment of boss""",
    'category': 'Calendar',
    'author': "Nguyen Duy Khanh",
    'company': 'Aardwolf Industries LLC',
    'website': "https://www.odoo.com/page/website-builder",
    'version': '12.0.1.0.0.1',
    'depends': ['base', 'board', 'calendar', 'contacts', 'hr', 'hr_holidays'],
    'data': [
        'security/new_group_security.xml',
        'views/board_views.xml',
        'views/calendar_views.xml',
        'views/mail_channel_views.xml',
        'views/hr_views.xml',
    ],
    'demo': [],
}