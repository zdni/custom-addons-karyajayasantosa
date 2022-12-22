from odoo import fields, models, api
from datetime import datetime, timedelta

import logging
_logger = logging.getLogger(__name__)

class AccountPayment(models.Model):
    _inherit = "account.payment"

    redeem_point = fields.Float('Redeem Point')
    redeem_amount = fields.Float('Amount Total from Redeem Point', readonly=True, compute='_calculate_redeem_amount')
    total_points = fields.Float('Remaining Points', readonly=True)
    redeem_status = fields.Boolean('Use Redeem Point', default=False)
    is_get_loyalty_point = fields.Boolean('Get Loyalty Point?', default=False)

    @api.one
    @api.depends('invoice_ids', 'amount', 'payment_date', 'currency_id')
    def _compute_payment_difference(self):
        # res = super(AccountPayment, self)._compute_payment_difference()
        if len(self.invoice_ids) == 0:
            return
        if self.invoice_ids[0].type in ['in_invoice', 'out_refund']:
            self.payment_difference = (self.amount-self.redeem_amount) - self._compute_total_invoices_amount()
        else:
            self.payment_difference = self._compute_total_invoices_amount() - (self.amount-self.redeem_amount)

        # return res        

    @api.onchange('communication')
    @api.depends('communication')
    def _redeem_status(self):
        for rec in self:
            for invoice in rec.invoice_ids:
                name = rec.invoice_ids[0].origin
                sale_order = self.env['sale.order'].search([
                    ('name', '=', name)
                ], limit=1)
                if sale_order:
                    if sale_order.redeem_status:
                        rec.redeem_status = True
                    else:
                        rec.redeem_status = False

                    if sale_order.is_get_loyalty_point:
                        rec.is_get_loyalty_point = True
                    else:
                        rec.is_get_loyalty_point = False
                else:
                    rec.redeem_status = False
                    rec.is_get_loyalty_point = False

                partner = rec.invoice_ids[0].partner_id
                if partner:
                    rec.total_points = partner.total_remaining_points
        

    @api.onchange('amount', 'redeem_amount')
    def _check_available_payment(self):
        for rec in self:
            if rec.amount + rec.redeem_amount > rec.invoice_ids[0].residual:
                return {
                    'warning': {
                        'title': 'Redeem Point',
                        'message': 'Point yang akan di redeem melewati total belanja!!!'
                    }
                }

    @api.multi
    @api.onchange('redeem_point')
    def _calculate_redeem_amount(self):
        return

    @api.multi
    @api.onchange('redeem_point')
    def onchange_redeem_point(self):
        for rec in self:
            if rec.redeem_point:
                rec.amount = rec.amount - (rec.redeem_point * rec.invoice_ids[0].partner_id.member_loyalty_level_id.to_amount)

                rec.payment_difference = 0.00
                
                total_points = rec.invoice_ids[0].partner_id.total_remaining_points
                if rec.redeem_point and rec.invoice_ids[0].partner_id.member_status:
                    if rec.redeem_point > total_points:
                        rec.redeem_point = 0.00
                        return {
                            'warning': {
                                'title': 'Redeem Point',
                                'message': 'Point yang akan di redeem melewati point yang dimiliki!!!'
                            }
                        }
                    rec.redeem_amount = rec.redeem_point * rec.invoice_ids[0].partner_id.member_loyalty_level_id.to_amount
                self._check_available_payment()
            else:
                rec.amount = rec.invoice_ids[0].residual - rec.payment_difference
                rec.redeem_amount = 0.00

    @api.multi
    def post(self):
        for rec in self:
            res = super(AccountPayment, self).post()

            user = self.env['res.users'].browse(self.env.uid)
            for invoice in self.invoice_ids:
                partner = invoice.partner_id
                member_loyalty = partner.member_loyalty_level_id
                name = invoice.origin
                
                sale_order = self.env['sale.order'].search([
                    ('name', '=', name)
                ], limit=1)

                if sale_order:

                    confirmation_date =  datetime.strptime(sale_order.confirmation_date.split()[0], '%Y-%m-%d')
                    payment_date =  datetime.strptime(self.payment_date, '%Y-%m-%d')
                    redeem_amount = self.redeem_point * member_loyalty.to_amount
                    if partner.member_status:
                        if sale_order.is_get_loyalty_point:
                        # if confirmation_date == payment_date:
                            if ((self.amount+redeem_amount) == sale_order.amount_total) and (self.amount-redeem_amount) >= member_loyalty.minimum_purchase:
                                if member_loyalty.type == 'percentage':
                                    earned_point = (sale_order.amount_total-redeem_amount) * member_loyalty.point_calculation_percentage / 100
                                if member_loyalty.type == 'fix':
                                    earned_point = member_loyalty.point_calculation_fix
                                if member_loyalty.type == 'fix_multiple':
                                    earned_point = ((sale_order.amount_total-redeem_amount)//member_loyalty.amount_multiple) * member_loyalty.point_calculation_fix_multiple
                                
                                point_vals = {
                                    'amount_total': (sale_order.amount_total-redeem_amount),
                                    'expired_date': datetime.now() + timedelta(days=member_loyalty.expired_day),
                                    'partner_id': partner.id,
                                    'points': earned_point,
                                    'sale_order_id': sale_order.id,
                                    'state': 'open',
                                    'source': 'so',
                                    'date_obtained': datetime.now(),
                                    'total_current_point': int( partner.total_remaining_points ) + int( earned_point ),
                                }
                                self.env['earned.point.record'].create(point_vals)
                        
                        if self.redeem_status:
                            self._check_available_payment()
                            if self.redeem_point > 0:
                                redeemed_vals = {
                                    'partner_id': self.invoice_ids[0].partner_id.id,
                                    'points': self.redeem_point,
                                    'redeem_amount': redeem_amount,
                                    'sale_order_id': sale_order.id,
                                    'date_used': datetime.now(),
                                }
                                self.env['redeem.point.record'].create(redeemed_vals)
                                last_earned_point = self.env['earned.point.record'].search([], limit=1, order="id desc").sudo()
                                last_earned_point.write({
                                    'total_current_point': int( last_earned_point.total_current_point ) - int( self.redeem_point )
                                })

                                # create journal redeem point
                                loyalty_journal_id = self.env['ir.values'].get_default('sale.config.settings', 'loyalty_journal_id') or 1
                                journal = self.env['account.journal'].search([
                                    ('id', '=', loyalty_journal_id )
                                ], limit=1)
                                payment = self.create_payment_loyalty(
                                    partner.id,
                                    journal,
                                    redeem_amount,
                                    self.payment_date,
                                    invoice.name, # self.communication,
                                    invoice.id,
                                )
                                for aml in payment.move_line_ids:
                                    if aml.credit != 0 and aml.credit == redeem_amount:
                                        invoice.assign_outstanding_credit(aml.id)
            return res

    def create_payment_loyalty(self, partner_id=None, journal=None, redeem_amount=0.00, payment_date=None, communication=None, invoice=None):
        payment_method = self.env.ref('account.account_payment_method_manual_in')

        name = self.env['ir.sequence'].with_context(ir_sequence_date=self.payment_date).next_by_code('account.payment.customer.invoice')
        payment_vals = {
            'invoice_ids': [invoice],
            'amount': redeem_amount or 0.00,
            'payment_date': payment_date,
            'communication': communication or '',
            'partner_id': partner_id,
            'partner_type': 'customer',
            'journal_id': journal.id,
            'payment_type': 'inbound',
            'payment_method_id': payment_method.id,
            'state': 'draft',
            'payment_difference_handling': 'open',
            'writeoff_account_id': False,
            'currency_id': self.currency_id.id,
            'name': name,
        }

        if self.env.context.get('tx_currency_id'):
            payment_vals['currency_id'] = self.env.context.get('tx_currency_id')
        
        payment = self.env['account.payment'].create(payment_vals)
        payment.post()
        return payment