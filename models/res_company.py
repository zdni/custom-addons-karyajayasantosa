from odoo import fields, models

class Company(models.Model):
    _inherit = 'res.company'

    location_store = fields.Many2one(
        'stock.location', string='Location Store')
    stock_store = fields.Many2one(
        'stock.warehouse', string='Stock Store')
    location_warehouse = fields.Many2one(
        'stock.location', string='Location Warehouse')
    stock_warehouse = fields.Many2one(
        'stock.warehouse', string='Stock Warehouse')
    location_transit = fields.Many2one(
        'stock.location', string='Location Transit')