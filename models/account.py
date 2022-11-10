from odoo import api, fields, models
from datetime import date, timedelta, datetime
import logging

_logger = logging.getLogger(__name__)

class AccountReportByCity(models.TransientModel):
    _name = 'report.turnover.city'

    city_ids = fields.Many2many("vit.kota", string='Kota', required=False)
    over_due = fields.Selection([
        ('30', '30 Hari'),
        ('60', '60 Hari'),
        ('90', '90 Hari'),
    ], 'Piutang Jatuh Tempo: ', default='30')
    
    @api.multi
    def print_report_turnover_by_city(self):
        groupby_dict = {}
        today = date.today()
        check_date = datetime.combine(today, datetime.min.time())
        over_due = int( self.over_due )

        if len(self.city_ids) == 0:
            self.city_ids = self.env['vit.kota'].search([])

        for city in self.city_ids:
            partners = self.env['res.partner'].search([('kota_id.name', '=', city.name)])
                        
            partner_detail = []
            for partner in partners:
                invoices = self.env['account.invoice'].search([ 
                    ('state', '=', 'open'), 
                    ('type', '=', 'out_invoice'), 
                    ('partner_id.name', '=', partner.display_name),
                    ('date_due', '<=', today) 
                ],
                order="date_invoice asc")

                
                partner_temp = []
                partner_invoices = []
                partner_temp.append(partner.display_name) #0
                partner_temp.append(partner.credit_limit) #1
                for invoice in invoices:
                    due_date = datetime.strptime(invoice.date_invoice, '%Y-%m-%d') + timedelta(days=over_due)
                    if due_date > check_date:
                        continue

                    partner_invoice = []
                    partner_invoice.append(invoice.date_invoice) #0
                    partner_invoice.append(invoice.number) #1
                    partner_invoice.append(invoice.date_due) #2
                    partner_invoice.append(invoice.origin) #3
                    partner_invoice.append(invoice.amount_total_signed ) #4
                    partner_invoice.append(invoice.residual_signed ) #5
                    partner_invoice.append(invoice.user_id.name) #6
                    partner_invoices.append(partner_invoice)

                partner_temp.append(partner_invoices)
                partner_temp.append(partner.risk_total) #3
                
                partner_temp.append(partner.risk_invoice_open) #5
                if len(partner_invoices) < 1:
                    continue
                partner_detail.append(partner_temp) #2

            if len(partner_detail) < 1:
                continue
            groupby_dict[city.name] = partner_detail

        datas = {
            'ids': self.ids,
            'model': 'report.turnover.city',
            'form': groupby_dict,

        }
        return self.env['report'].get_action(self,'report_turnover_by_city.temp_report_turnover_by_city', data=datas)