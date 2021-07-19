# -*- coding: utf-8 -*-
{
    'name': 'Aflowz School',
    "license": "LGPL-3",
    'summary': """
        Aflowz Schools Management
        """,
    'description': """
        Aflowz order
    """,
    'images': ['static/description/icon.png'],
    'author': "Aflowz",
    'website': "http://aflowz.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['mail'],
    'data': [
        'security/group.xml',
        'views/res_config_views.xml',
        'security/ir.model.access.csv',
        'views/aflowz_school_config_views.xml',
        'views/aflowz_school_class_views.xml',
        'views/aflowz_school_citizen_views.xml',
        'views/aflowz_school_event_views.xml',
        'views/aflowz_school_polling_views.xml',
        'views/aflowz_school_announcement_views.xml',
        'views/aflowz_school_menu.xml',
        'wizard/aflowz_class_move_wizard_views.xml'
    ]
}