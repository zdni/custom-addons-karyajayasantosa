# -*- coding: utf-8 -*-

{
    'name': 'Accounting Paid Invoices Report',
    'category': 'account',
    'version': '0.1',
    'summary': 'This module provides Accounting Paid Invoices Report',
    'author': 'Technoindo.com',
    'description': '''This module provides Accounting Paid Invoices Report.''',
    'depends': [
        'base', 
        'sale', 
        'account', 
        ],
    'data': [
        'views/report_view.xml',
        'report/invoice_temp.xml',
        'report/invoice_report.xml',
    ],
    'qweb': [
        # 'static/src/xml/cashback_templates.xml',
    ],
    'demo': [
        # 'demo/sale_agent_demo.xml',
    ],
    'images': ['static/description/banner.png'],
    'auto_install': False,
    'installable': True,
    'application': False,
}
