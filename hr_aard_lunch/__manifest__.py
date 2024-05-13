{
    'name': 'Aardwolf HR Lunch',
    'version': '12.0.1.0.0.1',
    'category': 'Human Resources',
    'summary': "Calculate Lunch automatic from Attendance",
    'description': """
    1. Create lunch rule to apply automatic for employee who has punching time
    2. Automatic calculate lunch based on employee's contracted working schedule and Attendance Total hours
        """,
    'author': "Nguyen Duy Khanh",
    'company': 'Aardwolf Industries LLC',
    'website': "",
    'depends': ['hr_employee_shift', 'hr_attendance', 'hr_aard_attendance_validation', 'hr_aard_overtime'],
    'data': ['security/ir.model.access.csv',
             'security/hr_lunch_security.xml',
             
             'views/aard_hr_lunch_view.xml',
             'views/aard_hr_lunch_rule_view.xml',
             'views/hr_attendance_view.xml'
             ],
    'demo': [
        'data/lunch_rule_data.xml',
        'data/overtime_rule_inherit_data.xml'
    ],
    'installable': True,
    'application': True,
}