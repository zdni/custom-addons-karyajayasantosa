{
    'name': "POS AUTHENTICATION ORDER OUT OF STOCK",
    'summary': """
        Lock order out of stock""",
    'description': """
        This module add features to lock order out of stock using password
    """,
    'author': "CV. TechnoIndo",
    'website': "www.technoindo.com",
    'category': 'Point Of Sale',
    'version': '10.0.1.0',
    'depends': ['base', 'point_of_sale', 'pos_sync_stock'],
    'data': [
        'views/assets.xml',
        'views/pos_config_view.xml',
    ],
}
