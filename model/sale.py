from odoo import api, fields, models
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

class SaleReport(models.TransientModel):
    _name = 'sale.salesperson_omset.report'

    start_date = fields.Date("Start Date", required=True) 
    end_date = fields.Date("End Date", required=True) 
    visible = fields.Boolean('Tampilkan Margin dan HPP')
    age = fields.Integer('Umur Piutang')
    salespersons = fields.Many2many('res.users', string="Salesperson")

    def get_data_hpp(self, origin):
        hpp = 0

        moves = self.env['stock.move'].search([
            ('picking_id.origin', '=', origin),
        ])
        for move in moves:
            for quant in move.quant_ids:
                hpp += quant.inventory_value

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

        invoices = self.env['account.invoice'].search([
            ('state', '=', 'paid'),
            ('paid_date', '>=', self.start_date),
            ('paid_date', '<=', self.end_date),
            ('user_id.id', 'in', array_salesperson_ids),
        ])
        for invoice in invoices:
            date_invoice = datetime.strptime(invoice.date_invoice, "%Y-%m-%d")
            paid_date = datetime.strptime(invoice.paid_date, "%Y-%m-%d")
            receivable_age = abs((paid_date - date_invoice).days)

            if receivable_age <= self.age:
                hpp = 0
                salesperson = invoice.user_id.name

                order = self.env['sale.order'].search([
                    ('name', '=', invoice.origin)
                ])

                data = [
                    invoice.partner_id.name,
                    invoice.origin,
                    invoice.date_invoice,
                    invoice.paid_date,
                    invoice.amount_total
                ]

                if self.visible:
                    hpp = self.get_data_hpp( invoice.origin )
                    
                    data.append( order.margin )
                    data.append( hpp )

                if data and salesperson:
                    if salesperson in dictionaryResult:
                        if data not in dictionaryResult[salesperson]:
                            dictionaryResult[salesperson].append( data )
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