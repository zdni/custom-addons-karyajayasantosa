# -*- coding: utf-8 -*-

{
    'name': 'Sale Stock Quant Check',
    'version': '1.0',
    'author': 'Technoindo.com',
    'category': 'Sales Management',
    'depends': [
        'sale',
        'stock',
        'sale_stock',
    ],
    'data': [
        # 'views/menu.xml',
        'views/sale_view.xml',
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