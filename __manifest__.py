{
    'name': 'Report Inventory',
    'author': 'CV. TechnoIndo',
    'category': 'Report',
    'version': '10.0',
    'summary': 'Report Inventory Adjustment XLSX and Report Detail Inventory',
    'depends': ['base', 'stock', 'report'],
    'data': [
        'reports/report.xml',
        'reports/report_inventory_detail.xml',
        'views/stock_inventory_views.xml',
        'wizards/inventory_detail_wizard.xml',
    ],
    'installable': True,
    'application': False,
}
