from odoo import api, fields, models, tools, _

import logging
_logger = logging.getLogger(__name__)

class StockInternalReorder(models.Model):
    _inherit = "stock.internal.reorder"

    # @api.multi
    @api.onchange('product_min_qty', 'product_max_qty')
    def product_qty_change(self):
        _logger.warning('product_qty_change')
        # self.product_id.min_stock = self.product_min_qty
        # self.product_id.max_stock = self.product_max_qty