{
    'name': 'Report Turnover By City',
    'category': 'account',
    'version': '0.1',
    'summary': 'This module provides Report Turnover By City.',
    'description': '''This module provides Report Turnover By City.'''
                   ,
    'depends': ['base', 'account', 'vit_kelurahan'],
    'data': [
        'views/account_view.xml',
        'report/report_turnover_by_city.xml',
        'report/temp_report_turnover_by_city.xml'
    ],
    'images': ['static/description/banner.png'],
    'auto_install': False,
    'installable': True,
    'application': False,
}
