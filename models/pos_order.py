from odoo import fields, models
from odoo.tools import float_is_zero

import logging
_logger = logging.getLogger(__name__)

class PosOrder(models.Model):
    _inherit = "pos.order"

    picking_address = fields.Char('Picking Address')

    def create_picking(self):
        res = super(PosOrder, self).create_picking()

        for order in self:
            moves = self.env['stock.move'].search([
                ('picking_id', '=', order.picking_id.id),
            ])
            if moves:
                index = 0
                for line in order.lines.filtered(lambda l: l.product_id.type in ['product', 'consu'] and not float_is_zero(l.qty, precision_rounding=l.product_id.uom_id.rounding)):
                    move = moves[index]
                    move.sudo().write({
                        'picking_note': line.picking_note,
                        'qty_picking': line.qty_picking,
                        'qty_picking_str': line.qty_picking_str,
                    })
                    index = index + 1

        return res