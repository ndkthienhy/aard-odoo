{
    'name': 'Aardwolf HR My Attendance',
    'version': '12.0.0.0.0.1',
    'summary': "Manage attendance for owner. Owner only show attendance self",
    'description': """
    Manage attendance for owner. Owner only show attendance self
    """,
    'category': 'Human Resources',
    'author': "Nguyen Duy Khanh",
    'company': 'Aardwolf Industries LLC',
    'website': "",
    'depends': ['hr_attendance', 'hr_aard_attendance_validation', 'hr_aard_lunch'],
    'data': [
        'views/hr_attendance_view.xml',

        'security/hr_attendance_security.xml',
        'security/ir.model.access.csv',
    ]
}