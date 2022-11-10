{
    'name': 'POS Retail',
    'category': 'Retail',
    'summary': 'Module Retail in Odoo 10',
    'description': """
    
""",
    'author': 'TechnoIndo',
    'website': 'http://www.technoindo.com',
    'version': '1.0.1',
    'depends': [
        'base',
        'point_of_sale',
        'sale',
        'pos_total_savings',
        'odoo_pos_keyboard',
    ],
    "data": [
        'data/ir_sequence_data.xml',
        'security/ir.model.access.csv',
        'views/assets.xml',
        'views/pos_config.xml',
        'views/pos_promotion.xml',
        'views/pos_discount_customer.xml',
        'views/pos_discount_global.xml',
        'views/pos_order.xml',
    ],
    'images': ['static/description/icon.png'],
    'qweb': [
        'static/src/xml/global_discount.xml',
        'static/src/xml/pos_promotion.xml',
        'static/src/xml/receipt.xml',
    ],
    'installable': True,
    'auto_install': False,
}