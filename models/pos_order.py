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
        process_line = partial(self.env['pos.order.line']._order_line_fields)
        return {
            'name':         ui_order['name'],
            'user_id':      ui_order['user_id'] or False,
            'session_id':   ui_order['pos_session_id'],
            'lines':        [process_line(l) for l in ui_order['lines']] if ui_order['lines'] else False,
            'pos_reference': ui_order['name'],
            'partner_id':   ui_order['partner_id'] or False,
            'date_order':   ui_order['creation_date'],
            'fiscal_position_id': ui_order['fiscal_position_id'],
            'percent_discount':   ui_order['percent_discount'] or False,
        } 