from odoo import fields, models, api
from datetime import datetime, timedelta
import logging
_logger = logging.getLogger(__name__)

class PosConfig(models.Model):
    _inherit = "pos.config"

    enable_pos_discount_global = fields.Boolean("Enable Global Discount")
    discount_global_product_id = fields.Many2one("product.product","Discount Product")