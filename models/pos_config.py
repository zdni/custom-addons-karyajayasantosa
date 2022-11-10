from odoo import fields, models, api

import logging
_logger = logging.getLogger(__name__)

class PosConfig(models.Model):
    _inherit = "pos.config"

    disc_product_id = fields.Many2one('product.product', string='Discount Product', required=True)
    
    enable_pos_discount_global = fields.Boolean("Enable Global Discount")
    min_order_disc_global = fields.Float('Minimum Order Disc Global')

    promotion_manual_select = fields.Boolean('Select Manual Promotion', default=True)
    promotion_ids = fields.Many2many('pos.promotion',
                                     'pos_config_promotion_rel',
                                     'config_id',
                                     'promotion_id',
                                     string='POS Promotion')