{
    "name": """Z Report POS""",
    "category": "Point of Sale",
    "summary": """Print Report Daily POS""",
    "author": "TechnoIndo",
    "website": "www.technoindo.com",
    "version": "10.0.1",
    "depends": ["point_of_sale"],
    "data": [
        "views/assets.xml", 
        "views/point_of_sale.xml", 
    ],
    'qweb' : [
        'static/src/xml/template.xml',
    ],
    'images': ['static/description/icon.png'],
    "installable": True,
    "auto_install": False,
}
