from itertools import groupby
from odoo import api, fields, models
from datetime import date, datetime, timedelta
import logging

_logger = logging.getLogger(__name__)

class SaleReport(models.TransientModel):
    _name = 'sale.salesperson_omset.report'

    start_date = fields.Date("Start Date", required=True) 
    end_date = fields.Date("End Date", required=True) 
    visible = fields.Boolean('Tampilkan Margin dan HPP')
    age = fields.Integer('Umur Piutang')
    salespersons = fields.Many2many('res.users', string="Salesperson")

    def get_data_hpp(self, number):
        hpp = 0

        move_lines = self.env['account.move.line'].search([
            ('move_id.name', '=', number),
            ('account_id.code', 'like', '5-')
        ])
        for move_line in move_lines:
            hpp += move_line.debit

        return hpp

    @api.multi
    def print_laporan_omset_margin(self):
        dictionaryResult = {}
        salesperson = ''
        array_salesperson_ids = []

        if len( self.salespersons ) < 1:
            self.salespersons = self.env['res.users'].search([])

        for salesperson in self.salespersons:
            array_salesperson_ids.append( salesperson.id )

        start_date = datetime.strptime( self.start_date, '%Y-%m-%d' ).date()
        due_date = ( start_date + timedelta((self.age+1)*-1 )).strftime('%Y-%m-%d')
        query = """
            SELECT mail_message.id AS mail_message_id, 
                mail_message.res_id AS mail_message_res_id, 
                account_invoice.origin, 
                account_invoice.date_invoice, 
                account_invoice.number, 
                mail_message.create_date, 
                date_part('day', mail_message.create_date - account_invoice.date_invoice) AS invoice_age
            FROM account_invoice
            JOIN mail_message ON mail_message.res_id = account_invoice.id
            WHERE account_invoice.state = 'paid'
            AND mail_message.id IN (SELECT MAX(mail_message.id) FROM mail_message WHERE mail_message.subtype_id = 4 GROUP BY mail_message.res_id)
            AND date_invoice <= %s
            AND date_invoice >= %s
            AND mail_message.create_date <= %s
            AND mail_message.create_date >= %s
            AND mail_message.subtype_id = 4
            AND date_part('day', mail_message.create_date - account_invoice.date_invoice) <= %s
            ORDER BY mail_message.create_date
        """
        params = [ self.end_date, due_date, self.end_date + ' 23:59:59', self.start_date, str( float( self.age ) ) ]

        self.env.cr.execute( query, params )
        invoices = self.env.cr.dictfetchall()
        
        for invoice in invoices:
            date_paid = self.env['mail.message'].search([
                ('subtype_id', '=', 4),
                ('res_id', '=', invoice['mail_message_res_id'])
            ], limit=1, order='id DESC')
            if date_paid.create_date == invoice['create_date'][:19]:
                hpp = 0

                order = self.env['sale.order'].search([ ('name', '=', invoice['origin']) ])
                salesperson = order.user_id.name
                if order.user_id.id in array_salesperson_ids:
                    data = [
                        order.partner_id.name,
                        order.name,
                        invoice['date_invoice'],
                        invoice['create_date'][:10],
                        order.amount_total,
                    ]

                    if self.visible:
                        hpp += self.get_data_hpp( invoice['number'] )
                        
                        data.append(order.margin)
                        data.append(hpp)

                    if data and salesperson:
                        if salesperson in dictionaryResult:
                            if data not in dictionaryResult[salesperson]:
                                dictionaryResult[salesperson].append(data)
                        else:
                            dictionaryResult[salesperson] = [data]

        datas = {
            'ids': self.ids,
            'model': 'sale.salesperson_omset.report',
            'form': dictionaryResult,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'visible': self.visible
        }
        return self.env['report'].get_action(self,'laporan_omset_margin_salesperson.omset_margin_temp', data=datas)