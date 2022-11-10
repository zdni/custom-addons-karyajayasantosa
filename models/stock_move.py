from odoo import fields, models

class StockMove(models.Model):
    _inherit = "stock.move"

    picking_note = fields.Char('Picking Note')
    qty_picking = fields.Float('Qty Picking')
    qty_picking_str = fields.Char('Qty Picking Str')