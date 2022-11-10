from odoo import api, fields, models, exceptions, _

class ProductCategory(models.Model):
    _inherit = 'product.category'

    is_consigment = fields.Boolean('Is Consigment')