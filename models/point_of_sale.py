from odoo import fields, models, api

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
    
# refund
class PosMakePayment(models.TransientModel):
    _inherit = 'pos.make.payment'

    @api.multi
    def check(self):
        res = super(PosMakePayment, self).check()

        self.ensure_one()
        refund = self.env['pos.order'].browse(self.env.context.get('active_id', False))
        data = self.read()[0]

        # check refund
        order = self.env['pos.order'].search([
            ('pos_reference', '=', refund.pos_reference),
        ])
        if len(order) > 1:
            if refund.session_id.config_id.enable_pos_deposit and refund.partner_id:
                if data['journal_id'][0] == refund.session_id.config_id.deposit_journal_id.id:
                    data = {
                        'partner_id': refund.partner_id.id,
                        'order_id': refund.id,
                        'date': refund.date_order,
                        'debit': data['amount']*-1 if data['amount'] < 0 else data['amount'],
                        'credit': 0,
                    }
                    self.env['account.deposit.line'].create(data)

        return res