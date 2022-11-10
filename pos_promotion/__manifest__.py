{
    'name': "POS Promo",
    'summary': """Module Promo in POS""",
    'description': """
        This module add features to create promo in POS 
    """,
    'author': "technoindo",
    'website': "www.techonoindo.com",
    'category': 'Point Of Sale',
    'license': "LGPL-3",
    'version': '10.0.1.0',
    'depends': [
        'point_of_sale',
        'product',
    ],
    'data': [
        'data/ir_sequence_data.xml',
        'security/ir.model.access.csv',
        'views/assets.xml',
        'views/pos_config.xml',
        'views/pos_order.xml',
        'views/pos_promotion.xml',
    ],
    'qweb': [
        'static/src/xml/pos_promotion.xml',
        'static/src/xml/receipt.xml',
    ]
}
