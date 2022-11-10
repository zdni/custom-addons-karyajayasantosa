from odoo import api, fields, models, _

import logging
_logger = logging.getLogger(__name__)

class Orderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    # @api.model
    # def _default_location_ids(self):
    #     location_ids = self.env['stock.location'].search([
    #         ('location_id.location_id.name', '=', 'TKTAS')
    #     ]).ids
    #     return location_ids

    location_ids = fields.Many2many(
        'stock.location',
        'order_location_rel',
        string='Gudang',
        # default=_default_location_ids,
    )
    warehouse_id = fields.Many2one(
        'stock.warehouse', 'Warehouse',
        ondelete="cascade", required=False)