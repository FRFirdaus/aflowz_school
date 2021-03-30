# -*- coding: utf-8 -*-
{
    'name': 'Aflowz Academic',
    "license": "LGPL-3",
    'summary': """
        Aflowz Academics Management
        """,
    'description': """
        Aflowz Academic
    """,
    'images': ['static/description/icon.png'],
    'author': "Aflowz",
    'website': "http://aflowz.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['mail', 'aflowz_school'],
    'data': [
        'security/group.xml',
        'security/ir.model.access.csv',
        'data/paper_format_data.xml',
        'views/aflowz_academic_subject_views.xml',
        'views/aflowz_academic_book_views.xml',
        'views/aflowz_academic_curriculum_views.xml',
        'views/aflowz_academic_raport_views.xml',
        'views/aflowz_academic_absence_views.xml',
        'views/aflowz_academic_tryout_views.xml',
        'views/aflowz_academic_menu.xml',
        'views/aflowz_academic_settings_views.xml',
        'views/aflowz_academic_report.xml',
        'views/report_academic.xml',
        'wizard/aflowz_raport_print_views.xml',
    ]
}