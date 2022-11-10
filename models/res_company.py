from odoo import fields, models

class Company(models.Model):
    _inherit = 'res.company'

    discount_product = fields.Many2one(
        'product.product', string='Discount Product')