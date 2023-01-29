from functools import partial

from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)

class PosOrder(models.Model):
    _inherit = 'pos.order'

    agent_id = fields.Many2one('res.partner', string='Agent')

    @api.model
    def _order_fields(self, ui_order):
        res = super(PosOrder, self)._order_fields(ui_order)
        res.update({
            'agent_id': ui_order['agent_id'] or False,
        })
        return res