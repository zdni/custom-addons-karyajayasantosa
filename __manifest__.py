{
    'name': 'POS Total Savings',
    'category': 'POS',
    'version': '0.1',
    'summary': 'Module to calculate saving pay in some order.',
    'depends': ['point_of_sale'],
    'data': [
        'views/assets.xml',
    ],
    'qweb': [
        'static/src/xml/*.xml'
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': False,
}
