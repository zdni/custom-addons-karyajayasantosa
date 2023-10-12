{
    'name': 'Deposit Customer',
    'category': 'Payment',
    'summary': 'Implement Deposit Customer in POS Order',
    'author': 'CV. TechnoIndo',
    'website': 'http://www.technoindo.com',
    'version': '1.0',
    'depends': [ 'base', 'point_of_sale', 'sale' ],
    "data": [
        'data/sequence.xml',

        'security/ir.model.access.csv',
        
        'views/account_deposit_views.xml',
        'views/deposit_customer_assets.xml',
        'views/point_of_sale_views.xml',
        'views/res_partner_views.xml',
    ],
    'images': ['static/description/icon.png'],
    'qweb': ['static/src/xml/pos.xml'],
    'installable': True,
    'auto_install': False,
}