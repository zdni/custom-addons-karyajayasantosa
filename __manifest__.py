# -*- coding: utf-8 -*-

{
    'name': "POS LOCK PRICE DISCOUNT",
    'summary': """
        Lock change price or discount in Point Of Sale""",
    'description': """
        This module add features to lock change price or discount in Point Of Sale using password
    """,
    'author': "Aimé Jules Andrinirina",
    'website': "",
    'category': 'Point Of Sale',
    'license': "LGPL-3",
    'version': '10.0.1.0',
    'images': ['static/description/banner.jpg'],
    'depends': ['base', 'point_of_sale'],
    'data': [
        'views/assets.xml',
        'views/pos_config_view.xml',
    ],
    'price': '0',
    'currency': 'EUR',
}
