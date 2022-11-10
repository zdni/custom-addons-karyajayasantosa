{
    'name': 'Landed Costs',
    'version': '1.1',
    'summary': 'Custom Landed Costs',
    'description': """
Landed Costs Management
=======================
This module allows you to easily add extra costs on pickings and decide the split of these costs among their stock moves in order to take them into account in your stock valuation.
    """,
    'website': 'technoindo.com',
    'depends': ['stock_account', 'purchase', 'stock_landed_costs'],
    'category': 'Warehouse',
    'data': [
        'security/ir.model.access.csv',
        'data/stock_landed_cost_data.xml',
        # 'views/product_views.xml',
        'views/custom_landed_cost_views.xml',
    ],
    'installable': True,
    'auto_install': False,
}
