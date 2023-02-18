from odoo import api, fields, models, exceptions, _
from datetime import date, datetime, timedelta

import logging
_logger = logging.getLogger(__name__)

class ReportBrandSales(models.TransientModel):
    _name = "report.brand.sales"

    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date('End Date', required=True)
    brand_ids = fields.Many2many('product.brand', string='Brand')

    @api.multi
    def print_report(self):
        array_brand = []
        if len(self.brand_ids) == 0:
            self.brand_ids = self.env['product.brand'].search([])
        for brand in self.brand_ids:
            array_brand.append( brand.id )

        groupby_dict = {}

        # SO transaction
        sale_order_lines = self.env['sale.order.line'].search([
            ('order_id.confirmation_date', '>=', self.start_date),
            ('order_id.confirmation_date', '<=', self.end_date),
            ('product_id.categ_id.is_consigment', '=', False),
            ('product_id.brand_id.id', 'in', array_brand),
        ])

        for sale_order_line in sale_order_lines:
            line = []

            line.append( sale_order_line.order_id.name )
            line.append( sale_order_line.order_id.confirmation_date )
            line.append( sale_order_line.product_id.name )
            line.append( sale_order_line.product_uom_qty )
            line.append( sale_order_line.price_unit )
            line.append( sale_order_line.price_subtotal )

            brand = sale_order_line.product_id.brand_id.name
            if brand in groupby_dict:
                groupby_dict[brand].append( line )
            else:
                groupby_dict[brand] = [line]
            
        # query = """
        #     SELECT mail_message.id AS mail_message_id, 
        #         mail_message.res_id AS mail_message_res_id, 
        #         mail_message.create_date, 
        #         account_invoice.origin, 
        #         account_invoice.date_invoice, 
        #         account_invoice.number, 
        #         account_invoice_line.id AS line_id,
        #         account_invoice_line.product_id
        #     FROM account_invoice
        #     JOIN mail_message ON mail_message.res_id = account_invoice.id
        #     JOIN account_invoice_line ON account_invoice_line.invoice_id = account_invoice.id
        #     WHERE account_invoice.state = 'paid'
        #     AND mail_message.id IN (SELECT MAX(mail_message.id) FROM mail_message WHERE mail_message.subtype_id = 4 GROUP BY mail_message.res_id)
        #     AND date_invoice <= %s
        #     AND date_invoice >= %s
        #     AND mail_message.create_date <= %s
        #     AND mail_message.create_date >= %s
        #     AND account_invoice.type = 'out_invoice'
        #     AND mail_message.subtype_id = 4
        #     ORDER BY mail_message.create_date
        # """
        # params = [ self.end_date, self.start_date, self.end_date + ' 23:59:59', self.start_date ]
        
        # self.env.cr.execute( query, params )
        # invoices = self.env.cr.dictfetchall()

        # for invoice in invoices:
        #     date_paid = self.env['mail.message'].search([
        #         ('subtype_id', '=', 4),
        #         ('res_id', '=', invoice['mail_message_res_id'])
        #     ], limit=1, order='id DESC')
        #     if date_paid.create_date == invoice['create_date'][:19]:
        #         line = []

        #         origin = invoice['origin']

        #         line_id = invoice['line_id']
        #         account_invoice_line = self.env['account.invoice.line'].search([
        #             ('id', '=', line_id),
        #             ('product_id.brand_id.id', 'in', array_brand),
        #             ('product_id.categ_id.is_consigment', '=', False)
        #         ], limit=1)
                
        #         if account_invoice_line:
        #             line.append( origin )
        #             line.append( invoice['create_date'] )
        #             line.append( account_invoice_line.product_id.name )
        #             line.append( account_invoice_line.quantity )
        #             line.append( account_invoice_line.price_unit )
        #             line.append( account_invoice_line.price_subtotal )

        #             brand = account_invoice_line.product_id.brand_id.name
        #             if brand in groupby_dict:
        #                 groupby_dict[brand].append( line )
        #             else:
        #                 groupby_dict[brand] = [line]

        # POS transaction
        pos_order_lines = self.env['pos.order.line'].search([
            ('order_id.date_order', '>=', self.start_date),
            ('order_id.date_order', '<=', self.end_date),
            ('product_id.categ_id.is_consigment', '=', False),
            ('product_id.brand_id.id', 'in', array_brand),
        ])

        for pos_order_line in pos_order_lines:
            line = []

            line.append( pos_order_line.order_id.name )
            line.append( pos_order_line.order_id.date_order )
            line.append( pos_order_line.product_id.name )
            line.append( pos_order_line.qty )
            line.append( pos_order_line.price_unit )
            line.append( pos_order_line.price_subtotal_incl )

            brand = pos_order_line.product_id.brand_id.name
            
            if brand in groupby_dict:
                groupby_dict[brand].append( line )
            else:
                groupby_dict[brand] = [line]

        datas = {
            'ids': self.ids,
            'model': 'report.brand.sales',
            'form': groupby_dict,
            'date': str(self.start_date) + ' sampai ' + str( self.end_date ),
        }
        return self.env['report'].get_action(self, 'report_brand_sales.report_temp', data=datas)