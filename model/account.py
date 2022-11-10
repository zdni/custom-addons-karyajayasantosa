from odoo import api, fields, models, exceptions, _
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

import logging
_logger = logging.getLogger(__name__)

class ReportAccountReceivableAge(models.TransientModel):
    _name = "report.account.receivable.age"

    # age = fields.Integer(string='Umur Piutang', required=True)
    start_age = fields.Integer(string='Umur Piutang (Awal)', required=True)
    end_age = fields.Integer(string='Umur Piutang (Akhir)', required=True)
    customers = fields.Many2many('res.partner', string='Pelanggan', required=False)
    city_ids = fields.Many2many("vit.kota", string='Kota', required=False)

    @api.multi
    def print_report_account_receivable_age(self):
        if self.start_age > self.end_age:
            raise exceptions.Warning(_('Akhir Umur Piutang tidak boleh lebih kecil dari Awal Umur Piutang'))
        if self.start_age < 0 or self.end_age < 0:
            raise exceptions.Warning(_('Inputan tidak boleh 0'))
        
        groupby_dict = {}

        if len(self.city_ids) == 0:
            self.city_ids = self.env['vit.kota'].search([])

        for city in self.city_ids:
            customers = self.env['res.partner'].search([('kota_id.name', '=', city.name)])

            today = date.today()
            start_date_invoice = ( today + timedelta( days=((self.start_age-1)*-1) ) ).strftime("%Y-%m-%d")
            end_date_invoice = ( today + timedelta( days=((self.end_age-1)*-1) ) ).strftime("%Y-%m-%d")
            # date_invoice = ( today + timedelta( days=(self.age*-1) ) ).strftime("%Y-%m-%d")

            customer_detail = []
            for customer in customers:
                invoices = self.env['account.invoice'].search([
                    # ('date_invoice', '>=', date_invoice),
                    ('date_invoice', '<=', start_date_invoice),
                    ('date_invoice', '>=', end_date_invoice),
                    ('partner_id', '=', customer.id),
                    ('state', 'in', ['draft', 'open']),
                    ('type', '=', 'out_invoice')
                ])
                customer_temp = []
                customer_invoices = []
                customer_temp.append(customer.display_name) #0
                customer_temp.append(customer.credit_limit) #1
                for invoice in invoices:
                    invoice_date = datetime.strptime(invoice.date_invoice, '%Y-%m-%d').date()
                    invoice_age = today - invoice_date

                    customer_invoice = []
                    customer_invoice.append(invoice.number)         #0
                    customer_invoice.append(invoice.payment_term_id.name)#1
                    customer_invoice.append( datetime.strptime(invoice.date_invoice, '%Y-%m-%d').strftime('%d-%m-%Y') )   #2
                    customer_invoice.append(invoice.user_id.name)   #3
                    customer_invoice.append( datetime.strptime(invoice.date_due, '%Y-%m-%d').strftime('%d-%m-%Y') )       #4
                    customer_invoice.append(invoice.amount_total)   #5
                    customer_invoice.append(invoice.residual)       #6
                    customer_invoice.append(invoice_age.days + 1)       #7
                    
                    bg_number = '-'
                    giros = self.env['vit.giro'].search([
                        ('giro_invoice_ids.invoice_id', '=', invoice.id)
                    ])
                    if giros:
                        for giro in giros:
                            bg_number = bg_number + ' ' + giro.name
                    customer_invoice.append(bg_number)              #8
                    
                    customer_invoices.append(customer_invoice)      
                
                customer_temp.append(customer_invoices) #2
                if len(customer_invoices) > 0:
                    customer_detail.append(customer_temp)

            if len(customer_detail) > 0:
                groupby_dict[city.name] = customer_detail
        
        datas = {
            'ids': self.ids,
            'model': 'report.account.receivable.age',
            'form': groupby_dict,
            'age': str(self.start_age) + ' sampai ' + str(self.end_age),
            'date': today.strftime('%d %b %Y'),
        }
        return self.env['report'].get_action(self,'report_account_receivable_age.report_temp', data=datas)

    
    def _prepare_report_account_receivable(self):
        self.ensure_one()
        today = date.today()
        return {
            'ids': self.ids,
            'model': 'report.account.receivable.age',
            'data': groupby_dict,
            'age': str(self.start_age) + ' sampai ' + str(self.end_age),
            'date': today.strftime('%d %b %Y'),
        }

    def _export(self, report_type):
        """Default export is PDF."""
        model = self.env['report_trial_balance_qweb']
        report = model.create(self._prepare_report_account_receivable())
        return report.print_report(report_type)