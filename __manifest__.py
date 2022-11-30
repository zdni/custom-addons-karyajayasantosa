{
    "name": """Member Card""",
    "category": "Sales",
    "summary": """Member Card for Customer""",
    "author": "TechnoIndo",
    "website": "www.technoindo.com",
    "version": "10.0.1",
    "depends": ["sale", "loyalty_point"],
    "data": [
        "data/ir_sequence_data.xml",
        "views/res_partner.xml", 
        "report/member_card.xml", 
    ],
    'images': ['static/description/icon.png'],
    "installable": True,
    "auto_install": False,
}
