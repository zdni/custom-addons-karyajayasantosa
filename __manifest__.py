{
    'name': 'Rule for field Stock Product',
    'author': 'technoindo.com',
    'category': 'hidden',
    'version': '10.0',
    'summary': 'Summary the addon.',
    'description': '''hidden field stock product to group selected'''
                   ,
    'depends': ['product', 'sale', 'hpp_stock_quant', 'sale_margin'],
    'data': [
        'views/product_template_view_inherit.xml',
        'views/sale_order_view_inherit.xml',
        'views/stock_product_template_view_inherit.xml'
    ],
    'images': [''],
    'auto_install': False,
    'installable': True,
    'application': False,
}
