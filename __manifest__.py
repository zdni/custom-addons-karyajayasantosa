# -*- coding: utf-8 -*-
{
    'name': 'Stock Internal Reordering',
    'version': '1.0',
    'author': 'Technoindo.com',
    'category': 'Stock Internal Reordering',
    'depends': [
        'stock',
    ],
    'data': [
        'views/menu.xml',
        'views/stock_internal_reorder.xml',

        'data/internal_reordering_data.xml',
        'data/cron_data.xml',
        
        'wizard/stock_internal_reorder_compute.xml',

        'security/ir.model.access.csv',
    ],
    'qweb': [
        # 'static/src/xml/cashback_templates.xml',
    ],
    'demo': [
        # 'demo/sale_agent_demo.xml',
    ],
    "installable": True,
	"auto_instal": False,
	"application": False,
}
