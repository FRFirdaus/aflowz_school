# -*- coding: utf-8 -*-
{
    'name': 'Aflowz School Demo Data',
    "license": "LGPL-3",
    'summary': """
        Aflowz School Demo Data
        """,
    'description': """
        Aflowz Academic Demo Data for school
    """,
    'images': ['static/description/icon.png'],
    'author': "Aflowz",
    'website': "http://aflowz.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['aflowz_school', 'aflowz_academic'],
    'data': [
        'data/grade_data.xml',
        'data/major_data.xml',
        'data/teacher_data.xml',
        'data/class_data.xml',
        'data/student_data.xml',
        'data/subject_data.xml',
        # 'data/book_data.xml',
        # 'data/curriculum_data.xml',
    ]
}