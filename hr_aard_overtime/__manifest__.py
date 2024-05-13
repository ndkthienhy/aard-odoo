{
    'name': 'Aardwolf HR Overtime',
    'version': '12.0.1.0.0.1',
    'category': 'Human Resources',
    'summary': "Calculate Overtime automatic from Attendance",
    'description': """
    1. Create overtime rule to apply automatic for employee who has punching time
    2. Automatic calculate overtime based on employee's contracted working schedule and Attendance
        Total overtime hours
        """,
    'author': "Nguyen Duy Khanh",
    'company': 'Aardwolf Industries LLC',
    'website': "",
    'depends': ['hr_employee_shift', 'hr_attendance', 'hr_aard_attendance_validation'],
    'data': ['security/ir.model.access.csv',
             'security/hr_overtime_security.xml',

             'views/aard_hr_overtime_view.xml',
             'views/aard_hr_overtime_rule_view.xml',
             'views/hr_attendance_view.xml'],
    'demo': [
        'data/overtime_rule_data.xml'
    ],
    'installable': True,
    'application': True,
}