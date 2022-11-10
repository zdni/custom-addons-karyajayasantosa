from odoo import api, fields, models, _

class PurchaseConfigSettings(models.TransientModel):
    _inherit = 'purchase.config.settings'

    company_discount_product_id = fields.Many2one(
        'product.product', related='company_id.discount_product', string='Discount Product',
        help='The product used to model the discount.')