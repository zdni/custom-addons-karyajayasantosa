{
    'name': 'Report Invoice Payment',
    'author': 'technoindo.com',
    'category': 'hidden',
    'version': '10.0',
    'summary': 'Summary the addon.',
    'description': '''Description the addon'''
                   ,
    'depends': ['account'],
    'data': [
        'reports/invoice_payment_report.xml',
        'reports/invoice_payment_temp.xml',
        'wizard/report_invoice_payment_wizard.xml',
    ],
    'images': [''],
    'auto_install': False,
    'installable': True,
    'application': False,
}
