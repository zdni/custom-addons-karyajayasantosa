from odoo import api, exceptions, fields, models, _
import logging
from datetime import date, timedelta

_logger = logging.getLogger(__name__)
class CommissionInvoices(models.Model):
    _name = "sale.commission.invoice"

    agent_id = fields.Many2many(
        comodel_name="res.partner",
        ondelete="restrict",
        string="Sales",
        domain="[('agent', '=', True)]"
    )
    day_term = fields.Integer(
        string="Umur Piutang",
        required=True,
        default=63 
    )
    start_date = fields.Date('Tanggal Awal', required=True )
    end_date = fields.Date('Tanggal Akhir', required=True )
    
    @api.multi
    def create_commission(self):
        self.ensure_one()
        settlement_obj = self.env['sale.commission.settlement']
        settlement_line_obj = self.env['sale.commission.settlement.line']
        settlement_ids = []

        date_to = date.today()
        date_from = date_to - timedelta(days=self.day_term)

        if not self.agent_id:
            self.agent_id = self.env['res.partner'].search(
                [('agent', '=', True)])
        payment_has_get = []
        for agent in self.agent_id:
            invoices = self.env['account.invoice'].search([
                ('date_invoice', '>=', date_from),
                ('date_invoice', '<=', date_to),
                ('user_id.name', '=', agent.name),
            ], order="date_invoice")

            list_payment = []
            for invoice in invoices:
                payments = self.env['account.payment'].search([
                    ('payment_date', '>=', self.start_date),
                    ('payment_date', '<=', self.end_date),
                    ('payment_type', '=', 'inbound'),
                    ('state', '=', 'posted'),
                    ('invoice_ids.number', '=', invoice.number),
                    ('settled', '=', False)
                ])

                for payment in payments:
                    if payment.id in payment_has_get:
                        continue
                    
                    payment_has_get.append(payment.id)
                    detail = []
                    detail.append(invoice)
                    detail.append(payment)
                    list_payment.append(detail)

            if len(list_payment):
                settlement = settlement_obj.create({
                    'agent': agent.id,
                    'date_from': self.start_date,
                    'date_to': self.end_date,
                })
                settlement_ids.append(settlement.id)

                for payment in list_payment:
                    settlement_line_obj.create({
                        'settlement': settlement.id,
                        'invoice': payment[0].id,
                        'payment': payment[1].id,
                        'date': payment[1].payment_date,
                        'total_payment': payment[1].amount})
                    
        if len(settlement_ids):
            return {
                'name': _('Created Settlements'),
                'type': 'ir.actions.act_window',
                'views': [[False, 'list'], [False, 'form']],
                'res_model': 'sale.commission.settlement',
                'domain': [['id', 'in', settlement_ids]],
            }

        else:
            return {'type': 'ir.actions.act_window_close'}