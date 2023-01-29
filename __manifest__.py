{
    'name': 'Marketing Agent',
    'version': '10.0',
    'author': 'TechnoIndo',
    'description': 'Set User to Marketing Agent',
    'category': 'Sales',
    'depends': ['point_of_sale'],
    'data': [
        'report/marketing_agent_report.xml',
        'report/report_template.xml',
        'views/assets.xml',
        'views/pos_order.xml',
        'views/res_partner.xml',
        'wizards/marketing_agent_report.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'website': 'www.tehcnoindo.com',
    'images': ['static/description/icon.png'],
    'qweb': [
        'static/src/xml/screens.xml',
    ]
}
