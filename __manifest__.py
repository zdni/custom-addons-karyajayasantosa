{
    'name': 'Laporan Omset dan Margin',
    'author': "TechnoIndo",
    'category': 'hidden',
    'version': '10.0',
    'summary': 'Laporan Omset dan Margin per Salesperson.',
    'description': '''Laporan Omset dan Margin per salesperson'''
                   ,
    'depends': ['base', 'sale'],
    'data': [
        'report/template.xml',
        'report/sale_temp.xml',
        'wizard/wizard.xml',
    ],
    'images': [''],
    'auto_install': False,
    'installable': True,
    'application': False,
}
