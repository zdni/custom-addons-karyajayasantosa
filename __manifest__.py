{
    'name': 'Schedule Pricelist Product',
    'category': 'Product',
    'summary': 'Module Schedule Pricelist Product',
    'description': """Module Schedule Pricelist Product""",
    'author': 'TechnoIndo',
    'website': 'http://www.technoindo.com',
    'version': '1.0',
    'depends': [
        'product',
        'purchase',
        'sale',
    ],
    "data": [
        'security/ir.model.access.csv',
        'views/product_template.xml',
        'views/schedule_pricelist_product.xml',
        'views/scheduler.xml',
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'auto_install': False,
}