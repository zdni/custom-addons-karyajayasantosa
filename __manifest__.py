# -*- coding: utf-8 -*-

{
    'name': "POS Global Discount",
    'summary': """Module Global Discount in POS""",
    'description': """
        This module add features to give global discount 
    """,
    'author': "technoindo",
    'website': "www.techonoindo.com",
    'category': 'Point Of Sale',
    'license': "LGPL-3",
    'version': '10.0.1.0',
    'depends': ['base', 'point_of_sale'],
    'data': [
        'views/assets.xml',
        'views/point_of_sale.xml',
        'views/pos_order.xml',
    ],
    'qweb': ['static/src/xml/global_discount.xml']
}
