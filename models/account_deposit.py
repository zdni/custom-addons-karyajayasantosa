from odoo import api, fields, models, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class AccountDepositLine(models.Model):
    _name = 'account.deposit.line'

    partner_id = fields.Many2one('res.partner', string='Customer')
    order_id = fields.Many2one('pos.order', string='POS Order')
    date = fields.Datetime('Date')
    debit = fields.Float('Debit')
    credit = fields.Float('Credit')