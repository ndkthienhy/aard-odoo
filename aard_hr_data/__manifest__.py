{
    'name': 'Aardwolf Human Resource Lunch',
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
    'depends': ['hr'],
    'data': ['security/ir.model.access.csv',
             'views/aard_hr_lunch_view.xml',
             'views/aard_hr_lunch_rule_view.xml',
             'data/employee_data.xml'],
    'demo': [],
    'installable': True,
    'application': True,
}