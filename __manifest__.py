{
    'name': 'Stock Quant in Product Template',
    'author': 'technoindo.com',
    'category': 'hidden',
    'version': '10.0',
    'summary': 'Summary the addon.',
    'description': '''Description the addon'''
                   ,
    'depends': ['product', 'stock', 'stock_internal_reordering'],
    'data': [
        'data/cron.xml',
        'views/product_template.xml',
        'views/stock_config_view.xml',
    ],
    'images': [''],
    'auto_install': False,
    'installable': True,
    'application': False,
}
