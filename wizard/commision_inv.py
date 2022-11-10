from odoo import api, exceptions, fields, models, _
import logging
from datetime import date, timedelta

_logger = logging.getLogger(__name__)
class CommissionInvoices(models.Model):
    _name = "sale.commission.invoice"

    agent_id = fields.Many2many(
        comodel_name="res.partner",
        ondelete="restrict",
        string="Agent",
        domain="[('agent', '=', True)]"
    )
    day_term = fields.Integer(
        string="Batas Jatuh Tempo",
        required=True,
        default=63 
    )
    date_to = fields.Date('Up to', required=True, default=fields.Date.today())
    
    @api.multi
    def create_commission(self):
        self.ensure_one()
        settlement_obj = self.env['sale.commission.settlement']
        settlement_line_obj = self.env['sale.commission.settlement.line']
        settlement_ids = []

        _date = fields.Date.from_string(self.date_to)
        if isinstance(_date, basestring):
            _date = fields.Date.from_string(_date)
        date_to = date(month=_date.month, year=_date.year, day=1)
        date_from = date_to - timedelta(days=self.day_term)

        if not self.agent_id:
            self.agent_id = self.env['res.partner'].search(
                [('agent', '=', True)])
        
        for agent in self.agent_id:
            invoices = self.env['account.invoice'].search(
                [('date_invoice', '>=', date_from),
                ('date_invoice', '<', date_to),
                ('user_id.name', '=', agent.name),
                ('state', '=', 'paid'),
                ('settled', '=', False)], order="date_invoice")

            if invoices:
                settlement = settlement_obj.create({
                    'agent': agent.id,
                    'date_from': date_from,
                    'date_to': date_to,
                })

                settlement_ids.append(settlement.id)
                for invoice in invoices:
                    settlement_line_obj.create({
                        'settlement': settlement.id,
                        'invoice': invoice.id,
                        'date': invoice.date_invoice,
                        'total_invoice': invoice.amount_total})

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