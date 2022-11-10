from odoo import fields, models, api
from datetime import datetime, timedelta
import logging
_logger = logging.getLogger(__name__)

class PosOrder(models.Model):
    _inherit = 'pos.order'

    tatal_bank_charge = fields.Float('Total Bank Charge')
    has_bank_charge = fields.Boolean('Has Bank Charge')

    @api.model
    def _process_order(self, order):
        res = super(PosOrder, self)._process_order(order)
        return res

# {
#     'fiscal_position_id': False, 
#     'partner_id': False, 
#     'user_id': 1, 
#     'name': u'Order 00841-002-0004', 
#     'pos_reference': u'Order 00841-002-0004', 
#     'date_order': u'2022-09-23 15:17:17', 
#     'lines': [
#         [0, 0, {
#             u'picking_note': u'', 
#             u'product_id': 9663, 
#             u'qty_picking': 0, 
#             u'price_unit': 3000, 
#             u'qty_picking_str': u'', 
#             u'qty': 1, 
#             u'pack_lot_ids': [], 
#             u'discount': 0, 
#             u'skip_check_price': False, 
#             u'id': 1, 
#             u'tax_ids': [[6, False, []]]
#         }],
#         [0, 0, {
#             u'picking_note': u'', 
#             u'product_id': '-', 
#             u'qty_picking': 0, 
#             u'price_unit': '-', 
#             u'qty_picking_str': u'', 
#             u'qty': 1, 
#             u'pack_lot_ids': [], 
#             u'discount': 0, 
#             u'skip_check_price': False, 
#             u'id': 1, 
#             u'tax_ids': [[6, False, []]]
#         }],
#     ], 
#     'session_id': 841
# }