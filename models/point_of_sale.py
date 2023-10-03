from odoo import fields, models, api
from datetime import datetime, timedelta

import logging
_logger = logging.getLogger(__name__)

class PosConfig(models.Model):
    _inherit = "pos.config"

    enable_pos_deposit = fields.Boolean("Enable Deposit POS")
    deposit_product_id = fields.Many2one("product.product","Deposit Product")
    deposit_journal_id = fields.Many2one('account.journal', string='Deposit Journal')

class PosOrder(models.Model):
    _inherit = 'pos.order'

    total_deposit = fields.Float('Total Deposit')

    @api.model
    def _order_fields(self, ui_order):
        res = super(PosOrder, self)._order_fields(ui_order)
        res.update({ 'total_deposit': ui_order.get('total_deposit') or 0.00 })
        return res
    
    @api.model
    def _process_order(self, order):
        res = super(PosOrder, self)._process_order(order)
        pos_session_id = order.get('pos_session_id')
        session = self.env['pos.session'].browse(pos_session_id)

        if session.config_id.enable_pos_deposit and res.partner_id:
            if(order.get('deposit_income') or order.get('deposit_redeemed')):
                deposit_income = order.get('deposit_income')
                deposit_redeemed = order.get('deposit_redeemed')
                
                if(order.get('deposit_income') < 0):
                    deposit_income = 0.00
                    deposit_redeemed = order.get('deposit_income') * -1
                
                data = {
                    'partner_id': res.partner_id.id,
                    'order_id': res.id,
                    'date': res.date_order,
                    'debit': deposit_income,
                    'credit': deposit_redeemed,
                }
                self.env['account.deposit.line'].create(data)

        return res