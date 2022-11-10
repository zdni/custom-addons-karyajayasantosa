 # -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

import logging

_logger = logging.getLogger(__name__)

class ProductStock(models.TransientModel):
    _name = "product.stock"

    order_line_id = fields.Many2one('sale.order.line', string='Order Line' )
    name = fields.Char(string="Name", size=100  )

    product_id = fields.Many2one('product.product', string='Product', domain=[('sale_ok', '=', True)], change_default=True, ondelete='restrict', required=True)
    location_id = fields.Many2one(
            'stock.location', 'Origin Location',
            ondelete="cascade" )
    stock_qty = fields.Float( string="Stock", default=0, digits=0 )
    