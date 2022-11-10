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
            partners = self.env['res.partner'].search([
                ('kota_id', '=', False),
                ('customer', '=', True),
            ])
            partner_detail = []
            for partner in partners:
                payments = self.env['account.payment'].search(
                [ 
                    ('payment_date', '<=', self.end_date),
                    ('payment_date', '>=', self.start_date),
                    ('payment_type', '=', 'inbound'),
                    ('state', '=', 'posted'),
                    ('partner_id.name', '=', partner.display_name) 
                ], 
                order="payment_date asc")
                
                partner_temp = []
                partner_payments = []
                
                partner_temp.append(partner.display_name) #0
                partner_temp.append(partner.credit_limit) #1
                
                for payment in payments:
                    partner_payment = []
                    total_disc = 0
                    
                    if payment.has_invoices:
                        if payment.communication:
                            partner_payment = self.info_invoice( payment )
                            if len(partner_payment):
                                partner_payments.append(partner_payment)
                        
                        elif payment.invoice_ids:
                            if len(payment.invoice_ids) == 1:
                                partner_payment.append(payment.invoice_ids.number) #0
                                partner_payment.append("") #1
                                partner_payment.append(payment.payment_date) #2
                                partner_payment.append(payment.amount) #3
                                partner_payment.append(payment.invoice_ids.amount_total) #4
                                partner_payment.append(payment.journal_id.name) #5
                            
                                partner_payments.append(partner_payment)
                            else:
                                total_invoices = 0
                                for invoice in payment.invoice_ids:
                                    total_invoices += invoice.amount_total

                                partner_payment.append(payment.name) #0
                                partner_payment.append("") #1
                                partner_payment.append(payment.payment_date) #2
                                partner_payment.append(payment.amount) #3
                                partner_payment.append(total_invoices) #4
                                partner_payment.append(payment.journal_id.name) #5

                                partner_payments.append(partner_payment)
                    
                    else:
                        if 'INV' in payment.communication or 'SO' in payment.communication:
                            partner_payment = self.info_invoice( payment )
                            if len(partner_payment):
                                partner_payments.append(partner_payment)
                        else:
                            payment_number = payment.name
                            origin = ""

                            partner_payment.append(payment_number) #0
                            partner_payment.append(origin) #1
                            partner_payment.append(payment.payment_date) #2
                            partner_payment.append(payment.amount) #3
                            partner_payment.append(payment.amount) #4
                            partner_payment.append(payment.journal_id.name) #5
                        
                            partner_payments.append(partner_payment)

                giros = self.env['vit.giro'].search(
                    [ 
                        ('clearing_date', '<=', self.end_date),
                        ('clearing_date', '>=', self.start_date),
                        ('type', '=', 'receipt'),
                        ('state', '=', 'close'),
                        ('partner_id.name', '=', partner.display_name) 
                    ], 
                    order="clearing_date asc")
                
                for giro in giros:
                    partner_payment = []
                    amount_invoices = 0
                    for line_invoice in giro.giro_invoice_ids:
                        invoice = self.env['account.invoice'].search([
                            ('number', '=', line_invoice.invoice_id.number),
                        ])
                        amount_invoices += line_invoice.invoice_id.amount_total
                        
                    partner_payment.append(giro.name) #0
                    partner_payment.append("") #1
                    partner_payment.append(giro.clearing_date) #2
                    partner_payment.append(giro.amount) #3
                    partner_payment.append(amount_invoices) #4
                    partner_payment.append(giro.journal_id.name) #5
                
                    partner_payments.append(partner_payment)

                if(len(partner_payments) == 0):
                    continue
                
                partner_temp.append(partner_payments)
                
                
                partner_temp.append(partner.risk_total) #3
                partner_temp.append(partner.risk_invoice_open) #4
                partner_detail.append(partner_temp) #2

            final_dict["Tanpa Kota"] = partner_detail
        
        for city in self.city_ids:
            partners = self.env['res.partner'].search([('kota_id.name', '=', city.name)])

            partner_detail = []
            for partner in partners:
                payments = self.env['account.payment'].search(
                [ 
                    ('payment_date', '<=', self.end_date),
                    ('payment_date', '>=', self.start_date),
                    ('payment_type', '=', 'inbound'),
                    ('state', '=', 'posted'),
                    ('partner_id.name', '=', partner.display_name) 
                ], 
                order="payment_date asc")
                
                partner_temp = []
                partner_payments = []
                
                partner_temp.append(partner.display_name) #0
                partner_temp.append(partner.credit_limit) #1
                
                for payment in payments:
                    partner_payment = []
                    total_disc = 0
                    
                    if payment.has_invoices:
                        if payment.communication:
                            partner_payment = self.info_invoice( payment )
                            if len(partner_payment):
                                partner_payments.append(partner_payment)
                        
                        elif payment.invoice_ids:
                            if len(payment.invoice_ids) == 1:
                                partner_payment.append(payment.invoice_ids.number) #0
                                partner_payment.append("") #1
                                partner_payment.append(payment.payment_date) #2
                                partner_payment.append(payment.amount) #3
                                partner_payment.append(payment.invoice_ids.amount_total) #4
                                partner_payment.append(payment.journal_id.name) #5
                            
                                partner_payments.append(partner_payment)
                            else:
                                total_invoices = 0
                                for invoice in payment.invoice_ids:
                                    total_invoices += invoice.amount_total

                                partner_payment.append(payment.name) #0
                                partner_payment.append("") #1
                                partner_payment.append(payment.payment_date) #2
                                partner_payment.append(payment.amount) #3
                                partner_payment.append(total_invoices) #4
                                partner_payment.append(payment.journal_id.name) #5

                                partner_payments.append(partner_payment)
                    
                    else:
                        if 'INV' in payment.communication or 'SO' in payment.communication:
                            partner_payment = self.info_invoice( payment )
                            if len(partner_payment):
                                partner_payments.append(partner_payment)
                        else:
                            payment_number = payment.name
                            origin = ""

                            partner_payment.append(payment_number) #0
                            partner_payment.append(origin) #1
                            partner_payment.append(payment.payment_date) #2
                            partner_payment.append(payment.amount) #3
                            partner_payment.append(payment.amount) #4
                            partner_payment.append(payment.journal_id.name) #5
                        
                            partner_payments.append(partner_payment)

                giros = self.env['vit.giro'].search(
                    [ 
                        ('clearing_date', '<=', self.end_date),
                        ('clearing_date', '>=', self.start_date),
                        ('type', '=', 'receipt'),
                        ('state', '=', 'close'),
                        ('partner_id.name', '=', partner.display_name) 
                    ], 
                    order="clearing_date asc")
                
                for giro in giros:
                    partner_payment = []
                    amount_invoices = 0
                    for line_invoice in giro.giro_invoice_ids:
                        invoice = self.env['account.invoice'].search([
                            ('number', '=', line_invoice.invoice_id.number),
                        ])
                        amount_invoices += line_invoice.invoice_id.amount_total
                        
                    partner_payment.append(giro.name) #0
                    partner_payment.append("") #1
                    partner_payment.append(giro.clearing_date) #2
                    partner_payment.append(giro.amount) #3
                    partner_payment.append(amount_invoices) #4
                    partner_payment.append(giro.journal_id.name) #5
                
                    partner_payments.append(partner_payment)

                if(len(partner_payments) == 0):
                    continue
                
                partner_temp.append(partner_payments)
                
                
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

    def info_invoice(self, payment):
        temp = []
        total_disc = 0
        invoices = {}

        memo_type = payment.communication
        if memo_type:
            if 'INV' in memo_type:
                invoices = self.env['account.invoice'].search([
                    ('number', '=', memo_type.split('-')[0].strip()),
                    # ('state', '=', 'paid')
                ])
                so = self.env['sale.order'].search([
                    ('name', '=', invoices.origin)
                ])

            elif 'SO' in memo_type:
                so = self.env['sale.order'].search([
                    ('name', '=', memo_type.split('-')[0].strip())
                ])
                invoices = self.env['account.invoice'].search([
                    ('origin', '=', so.name),
                    # ('state', '=', 'paid')
                ])

        for invoice in invoices:
            origin = invoice.origin

            temp.append(invoice.number) #0
            temp.append(origin) #1
            temp.append(payment.payment_date) #2
            temp.append(payment.amount) #3
            temp.append(invoice.amount_total) #4
            temp.append(payment.journal_id.name) #5

        return temp