{
    'name': 'Internal Transfer Report',
    'category': 'stock',
    'version': '0.1',
    'summary': 'This module provides Internal Transfer Report.',
    'description': '''This module provides Internal Transfer Report.'''
                   ,
    'depends': ['base', 'stock'],
    'data': [
        'views/internal_report_view.xml',
        'report/internal_report.xml',
        'report/internal_transfer_report_temp.xml'
    ],
    'images': ['static/description/banner.png'],
    'auto_install': False,
    'installable': True,
    'application': False,
}
