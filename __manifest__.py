{
    'name': "POS Picking Note",
    'summary': """Module note orderline in POS""",
    'description': """
        This module add features to add note in each orderline which product have to delivery to customer's home 
    """,
    'author': "technoindo",
    'website': "www.techonoindo.com",
    'category': 'Point Of Sale',
    'license': "LGPL-3",
    'version': '10.0.1.0',
    'depends': ['base', 'point_of_sale', 'odoo_pos_keyboard', 'dotmatrix', 'stock'],
    'data': [
        'views/assets.xml',
        'views/point_of_sale.xml',
        'views/stock_picking.xml',
    ],
    'qweb': ['static/src/xml/pos_picking_note.xml']
}
