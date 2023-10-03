from odoo import fields, models

class Company(models.Model):
    _inherit = 'res.company'

    deposit_product = fields.Many2one('product.product', string='Deposit Product')