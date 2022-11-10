from odoo import api, fields, models, _

class StockConfigSettings(models.TransientModel):
    _inherit = 'stock.config.settings'

    # Toko
    company_location_store_id = fields.Many2one(
        'stock.location', related='company_id.location_store', string='Location Store',
        help='The warehouse used to model the store.')
    company_stock_store_id = fields.Many2one(
        'stock.warehouse', related='company_id.stock_store', string='Stock Store',
        help='The stock used to model the store.')

    # Gudang
    company_location_warehouse_id = fields.Many2one(
        'stock.location', related='company_id.location_warehouse', string='Location Warehouse',
        help='The location used to model the warehouse.')
    company_stock_warehouse_id = fields.Many2one(
        'stock.warehouse', related='company_id.stock_warehouse', string='Stock Warehouse',
        help='The stock used to model the warehouse.')

    # Transit
    company_location_transit_id = fields.Many2one(
        'stock.location', related='company_id.location_transit', string='Location Transit',
        help='The location used to model the transit.')