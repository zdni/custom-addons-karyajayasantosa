{
    'name': 'Reprot Product Consigment',
    'author': 'TechnoIndo',
    'category': 'Report',
    'version': '10.0',
    'summary': 'Report Product Consigment.',
    'depends': ['base', 'sale', 'account', 'product', 'report', 'product_brand', 'product_category_consigment'],
    'data': [
        'reports/menu_report.xml',
        'reports/report_temp.xml',
        'wizard/report_product_consigment.xml',
    ],
    'installable': True,
    'application': False,
}
