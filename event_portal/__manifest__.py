# -*- coding: utf-8 -*-
{
    'name': 'Events Portal Test',
    'version': '1.1',
    'category': 'Test',
    'summary': 'List of all events',
    'description': "List of all events",
    'depends': ['event', 'portal'],
    'data': [
        'views/event_portal_templates.xml',
        'report/event_portal_report.xml'
    ],
    'assets': {
        'web.assets_frontend': [
            'event_portal/static/src/js/event_portal_sidebar.js',
        ]
    },
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
