{
    'name': 'Aardwolf HR Attendance Validation',
    'version': '12.0.0.0.0.1',
    'summary': "Validation and Calculation of valid attendance (according to work schedule)",
    'description': """
    1. Automatic calculate late coming and early leave based on employee's contracted working schedule
        Total late coming hours
        Total early leave hours
        Total valid attendance hours (within contracted working schedule)
    2. If enabled, automatic fill in missing check-out and mark the entry as "Auto-Checkout" for later tracking
        Missing check-out attendance entries will be automatically checked out after 10 hours counting from the time of expected valid checkout
    """,
    'category': 'Human Resources',
    'author': "Nguyen Duy Khanh",
    'company': 'Aardwolf Industries LLC',
    'website': "https://www.toolrange.com.vn/",
    'depends': ['hr_attendance', 'hr_employee_shift'],
    'data': [
        'views/hr_attendance_view.xml',
        'views/res_config_settings_views.xml',

        'security/hr_attendance_security.xml',
    ]
}