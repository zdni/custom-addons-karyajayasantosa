# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class PosVoucher(models.Model):
    _name = 'pos.voucher'

    name = fields.Char('Name', required=True)
    code = fields.Char('Code', required=True)
    amount = fields.Float('Amount', required=True, default=0)
    minimum_purchase = fields.Float('Minimum Purchase', required=True, default=0)
    expiry_date = fields.Date('Expiry Date')
    # pos_order_id = fields.Many2one('pos.order', string='Pos Order', readonly=True)

