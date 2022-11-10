from odoo import api, fields, models

class ProductBrand(models.Model):
    _name = 'product.brand'
    _description = "Product Brand"
    _order = "sequence, name"

    name = fields.Char('Name')
    sequence = fields.Integer(help="Gives the sequence order when displaying a list of product brands.")
