from odoo import api, fields, models, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class AccountDepositLine(models.Model):
    _name = 'account.deposit.line'

    name = fields.Char(string='Name', readonly=True, default='/')
    partner_id = fields.Many2one('res.partner', string='Customer')
    order_id = fields.Many2one('pos.order', string='Reference', required=True)
    date = fields.Datetime('Date', required=True)
    debit = fields.Float('Debit', default=0)
    credit = fields.Float('Credit', default=0)

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('account.deposit.line')
        return super(AccountDepositLine, self).create(vals)