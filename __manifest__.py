{
    'name': 'Sales Report By Customer',
    'category': 'sale',
    'version': '0.1',
    'summary': 'This module provides Sales Report By Customer.',
    'website': ' ',
    'author': 'Sitaram',
    'license': 'AGPL-3',
    'description': '''This module provides Sales Report By Customer.'''
                   ,
    'depends': ['base', 'sale'],
    'data': [
        'views/sale_view.xml',
        'report/so_report.xml',
        'report/so_temp.xml'
    ],
    'images': ['static/description/banner.png'],
    'auto_install': False,
    'installable': True,
    'application': False,
}
