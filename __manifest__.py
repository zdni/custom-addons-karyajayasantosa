{
    'name': 'Due Date Invoice Check',
    'author': "TechnoIndo",
    'category': 'hidden',
    'version': '10.0',
    'summary': 'Addon for check if customer have invocie which due date.',
    'description': '''Addon for check if customer have invocie which due date, and change state of sale_warn to block if true''',
    'depends': ['base', 'account', 'partner_financial_risk', 'sale'],
    'data': [
        'data/cron.xml',
        'view/customer.xml',
        'view/sale_warn_config.xml',
        'security/ir.model.access.csv',
    ],
    'images': [''],
    'auto_install': False,
    'installable': True,
    'application': False,
}
