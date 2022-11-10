from odoo import api, fields, models, _
from datetime import date, timedelta, datetime
import logging

_logger = logging.getLogger(__name__)
class CheckInvoices(models.Model):
    _name = 'account.invoice'
    _inherit = 'account.invoice'

    @api.model
    def _cron_check_invoice(self):
        today = date.today()
        partner_ids_block = []
        invoices = self.env['account.invoice'].search([
            ('date_due', '<=', today),
            ('state', '=', 'open')
        ])

        for invoice in invoices:
            partner = invoice.partner_id
            
            due_date_customer = partner.due_date_customer
            due_date = datetime.strptime(invoice.date_invoice, '%Y-%m-%d') + timedelta(days=due_date_customer)
            
            check_date = datetime.combine(today, datetime.min.time())

            if due_date < check_date:
                self.env['res.partner'].search([
                    ('id', '=', partner.id)
                ]).sudo().write({
                    'sale_warn': 'block',
                    'sale_warn_msg': 'Ada tagihan jatuh tempo',
                })
                if partner.id not in partner_ids_block:
                    partner_ids_block.append(partner.id)

        partners_block = self.env['res.partner'].search([
            ('sale_warn', '=', 'block'),
            ('id', 'not in', partner_ids_block)
        ])
        partners_block.sudo().write({'sale_warn': 'no-message'})