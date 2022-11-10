{
    'name': 'Custom Reordering Rules',
    'author': 'technoindo.com',
    'category': 'hidden',
    'version': '10.0',
    'summary': 'Summary the addon.',
    'description': '''Module Custom Reordering Rules
    make calculation for trigger the reordering document run to many2many
    '''
                   ,
    'depends': ['stock', 'procurement'],
    'data': [
        'views/view_warehouse_orderpoint_form_inherit.xml'
    ],
    'images': [''],
    'auto_install': False,
    'installable': True,
    'application': False,
}
