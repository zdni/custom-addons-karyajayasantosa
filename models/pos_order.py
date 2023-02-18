from odoo import fields, models, api
from datetime import datetime, timedelta
from functools import partial

import logging
_logger = logging.getLogger(__name__)

class PosOrder(models.Model):
    _inherit = "pos.order"

    percent_discount = fields.Float(string='Discount (%)')

    @api.model
    def _order_fields(self, ui_order):
        res = super(PosOrder, self)._order_fields(ui_order)
        res.update({
            'percent_discount':   ui_order['percent_discount'] or False,
        })
        return res