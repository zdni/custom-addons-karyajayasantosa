# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _

class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    picking_note = fields.Char('Picking Note')
    qty_picking = fields.Float('Qty Picking')
    qty_picking_str = fields.Char('Qty Picking Str')