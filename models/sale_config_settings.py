from odoo import api, fields, models, _

class PurchaseConfigSettings(models.TransientModel):
    _inherit = 'sale.config.settings'

    company_deposit_product_id = fields.Many2one(
        'product.product', related='company_id.deposit_product', string='Deposit Product',
        help='The product used to model the deposit.')