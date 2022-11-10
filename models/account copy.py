from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)

class ReportInvoicePayment(models.TransientModel):
    _name = 'report.invoice.payment'

    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date(string="End Date", required=True)
    city_ids = fields.Many2many("vit.kota", string='Kota', required=False)

    @api.multi
    def print_report_invoice_payment(self):
        final_dict = {}

        if len(self.city_ids) == 0:
            self.city_ids = self.env['vit.kota'].search([])

        for city in self.city_ids:
            partners = self.env['res.partner'].search([('kota_id.name', '=', city.name)])

            partner_detail = []
            for partner in partners:
                invoices = self.env['account.invoice'].search([ 
                    ('date_invoice', '<=', self.end_date), 
                    ('date_invoice', '>=', self.start_date), 
                    ('state', '=', 'paid'), 
                    ('type', '=', 'out_invoice'), 
                    ('partner_id.name', '=', partner.display_name) 
                ],
                order="date_invoice asc")
                partner_temp = []
                partner_invoices = []
                partner_temp.append(partner.display_name) #0
                partner_temp.append(partner.credit_limit) #1
                for invoice in invoices:
                    partner_invoice = []
                    partner_invoice.append(invoice.date_invoice) #0
                    partner_invoice.append(invoice.number) #1
                    partner_invoice.append(invoice.date_due) #2
                    partner_invoice.append(invoice.origin) #3
                    partner_invoice.append(invoice.amount_total_signed ) #4
                    partner_invoice.append(invoice.user_id.name) #5

                    sale = self.env['sale.order'].search([
                        ('name', '=', invoice.origin)
                    ])
                    partner_invoice.append(sale.discount_total) #6

                    payments = self.env['account.payment'].search([
                        ('communication', '=', invoice.number)
                    ])
                    type_payment = ''
                    if(len(payments) == 1):
                        type_payment = dict(payments.journal_id._fields['type'].selection).get(payments.journal_id.type)
                    else:
                        for payment in payments:
                            type_payment = dict(payment.journal_id._fields['type'].selection).get(payment.journal_id.type)
                        
                    partner_invoice.append(type_payment) #7

                    partner_invoices.append(partner_invoice)

                if(len(partner_invoices) == 0):
                    continue
                partner_temp.append(partner_invoices)
                partner_temp.append(partner.risk_total) #3
                
                partner_temp.append(partner.risk_invoice_open) #4
                partner_detail.append(partner_temp) #2


            final_dict[city.name] = partner_detail

        datas = {
            'ids': self.ids,
            'model': 'report.invoice.payment',
            'form': final_dict,
            'start_date': self.start_date,
            'end_date': self.end_date,

        }
        return self.env['report'].get_action(self,'report_invoice_payment.invoice_payment_temp', data=datas)


    def _prepare_report_trial_balance(self):
        self.ensure_one()
        return {
            'ids': self.ids,
            'model': 'report.invoice.payment',
            'data': final_dict,
            'start_date': self.start_date,
            'end_date': self.end_date,
        }

    def _export(self, report_type):
        """Default export is PDF."""
        model = self.env['report_trial_balance_qweb']
        report = model.create(self._prepare_report_trial_balance())
        return report.print_report(report_type)