from odoo import api, fields, models, tools, _

import logging
_logger = logging.getLogger(__name__)

class StockWarehouseOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    # @api.one
    @api.onchange('product_min_qty', 'product_max_qty')
    def product_qty_change(self):
        self.ensure_one()
        _logger.warning( "change product qty" )
        self.product_id.min_stock = self.product_min_qty
        self.product_id.max_stock = self.product_max_qty
    
    # @api.one
    @api.onchange('location_ids')
    def location_ids_change(self):
        self.ensure_one()
        _logger.warning( "change product qty" )
        self.product_id.location_ids = self.location_ids