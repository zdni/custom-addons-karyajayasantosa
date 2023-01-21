from odoo import fields, models

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    not_earn_loyatly_point = fields.Boolean('Not Earn Loyalty Point')