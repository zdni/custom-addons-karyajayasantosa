{
    'name': 'Product Brand',
    'version': '10.0',
    'author': 'TechnoIndo',
    'description': 'Allow define brand for product',
    'category': 'Sales',
    'depends': ['sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_brand.xml',
        'views/product_template.xml',
    ],
    'installable': True,
    'website': 'www.tehcnoindo.com',
    'images': ['static/description/icon.png'],
}
