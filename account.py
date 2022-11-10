from odoo import api, fields, models
import ast
import logging

_logger = logging.getLogger(__name__)

class ProfitCollectionReport(models.TransientModel):
    _name = 'account.profit.report'

    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date(string="End Date", required=True)
    
    @api.multi
    def print_profit_coll_report(self):
        payments = self.env['account.payment'].search(
            [ 
                ('payment_date', '<=', self.end_date),
                ('payment_date', '>=', self.start_date),
                ('payment_type', '=', 'inbound'),
                ('state', '=', 'posted'),
            ], 
            order="payment_date asc")

        payment_data = []
        for payment in payments:
            temp = []
            total_hpp = 0
            hpp_payment = 0
            total_disc = 0
            
            if payment.has_invoices:
                if payment.communication:
                    temp = self.count_hpp( payment )
                    if len(temp):
                        payment_data.append(temp)
            else:
                if 'INV' in payment.communication or 'SO' in payment.communication:
                    temp = self.count_hpp( payment )
                    if len(temp):
                        payment_data.append(temp)
                else:
                    margin = payment.amount - hpp_payment
                    payment_number = payment.name
                    origin = ""

                    temp.append(payment_number) #0
                    temp.append(origin) #1
                    temp.append(payment.payment_date) #2
                    temp.append(payment.partner_id.display_name) #3
                    temp.append(total_disc) #4
                    temp.append(payment.amount) #5
                    temp.append(hpp_payment) #6
                    temp.append(margin) #7
                    temp.append(total_hpp) #8
                    temp.append(payment.amount) #9
                
                    payment_data.append(temp)
            
        giros = self.env['vit.giro'].search(
            [ 
                ('clearing_date', '<=', self.end_date),
                ('clearing_date', '>=', self.start_date),
                ('type', '=', 'receipt'),
                ('state', '=', 'close'),
            ], 
            order="clearing_date asc")
        
        for giro in giros:
            hpp_giro = 0
            total_hpp = 0
            amount_invoices = 0
            for line_invoice in giro.giro_invoice_ids:
                invoice = self.env['account.invoice'].search([
                    ('number', '=', line_invoice.invoice_id.number),
                ])
                hpp_payment = 0
                hpp_per_products = self.env['account.move.line'].search([
                    ('move_id', '=', invoice.move_id.id),
                    ('account_id.code', 'like', '5-'),
                ],
                order="account_id asc")
                
                debit_hpp = 0
                for hpp_per_product in hpp_per_products:
                    debit_hpp += hpp_per_product.debit
                
                hpp_payment += debit_hpp
                total_hpp += hpp_payment

                amount_invoices += line_invoice.amount_invoice
                
                percent = (line_invoice.amount*100) / line_invoice.amount_invoice
                if percent <= 100:
                    hpp_payment = (hpp_payment*percent)/100
                hpp_giro += hpp_payment


            temp = []
            temp.append(giro.name) #0
            temp.append("") #1
            temp.append(giro.clearing_date) #2
            temp.append(giro.partner_id.display_name) #3
            temp.append(0) #4
            temp.append(giro.amount) #5
            temp.append(hpp_giro) #6
            temp.append(giro.amount - hpp_giro) #7
            temp.append(total_hpp) #8
            temp.append(amount_invoices) #9
        
            payment_data.append(temp)
        
        datas = {
            'ids': self.ids,
            'model': 'invoice.profit.report',
            'form': payment_data,
            'start_date': self.start_date,
            'end_date': self.end_date,

        }
        return self.env['report'].get_action(self,'profit_collection_report.account_report_temp', data=datas)

    def count_hpp(self, payment):
        temp = []
        total_hpp = 0
        hpp_payment = 0
        total_disc = 0

        memo_type = payment.communication
        if memo_type:
            if 'INV' in memo_type:
                invoices = self.env['account.invoice'].search([
                    ('number', '=', memo_type.split('-')[0].strip()),
                    ('state', '=', 'paid')
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
                    ('state', '=', 'paid')
                ])

        for invoice in invoices:
            for invoice_line in invoice.invoice_line_ids:
                total_disc += invoice_line.discount

            hpp_per_products = self.env['account.move.line'].search([
                    ('move_id', '=', invoice.move_id.id),
                    ('account_id.code', 'like', '5-'),
                ],
            order="account_id asc")
            
            debit_hpp = 0
            for hpp_per_product in hpp_per_products:
                debit_hpp += hpp_per_product.debit

            hpp_payment += debit_hpp
            total_hpp = hpp_payment

            total_so = so.amount_total
            percent = (invoice.amount_total*100) / total_so

            if percent <= 100:
                hpp_payment = (hpp_payment*percent)/100

            if memo_type:
                count_payment = self.env['account.move'].search_count([
                    ('ref', 'like', memo_type.split('-')[0].strip())
                ])
                payment_with_giro = self.env['vit.giro_invioce'].search_count([
                    ('invoice_id.number', '=', memo_type.split('-')[0].strip())
                ])
                # 0783
                if((count_payment+payment_with_giro) > 1):
                    percent = (payment.amount*100) / invoice.amount_total
                    if percent <= 100:
                        hpp_payment = (hpp_payment*percent)/100

            margin = payment.amount - hpp_payment

            payment_number = payment.communication
            origin = invoice.origin

            temp.append(invoice.number) #0
            temp.append(origin) #1
            temp.append(payment.payment_date) #2
            temp.append(payment.partner_id.display_name) #3
            temp.append(total_disc) #4
            temp.append(payment.amount) #5
            temp.append(hpp_payment) #6
            temp.append(margin) #7
            temp.append(total_hpp) #8
            temp.append(invoice.amount_total) #9

        return temp