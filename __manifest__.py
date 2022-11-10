# -*- coding: utf-8 -*-

{
    'name': "POS Bank Charge",
    'summary': """Module Bank Charge in POS""",
    'description': """
        This module add features to add bank charge 
    """,
    'author': "technoindo",
    'website': "www.techonoindo.com",
    'category': 'Point Of Sale',
    'license': "LGPL-3",
    'version': '10.0.1.0',
    'depends': ['base', 'point_of_sale', 'odoo_pos_keyboard'],
    'data': [
        'security/ir.model.access.csv',
        'views/assets.xml',
        'views/point_of_sale.xml',
        'views/pos_bank_charge.xml',
    ],
    'qweb': ['static/src/xml/pos_bank_charge.xml']
}
