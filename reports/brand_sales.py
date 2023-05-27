from odoo import api, fields, models, exceptions, _
from datetime import date, datetime, timedelta

import logging
_logger = logging.getLogger(__name__)

class ReportBrandSales(models.TransientModel):
    _name = "report.brand.sales"

    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date('End Date', required=True)
    brand_ids = fields.Many2many('product.brand', string='Brand')
    type = fields.Selection([
        ('all', 'Semua'),
        ('sale', 'Sale Order'),
        ('pos', 'Point of Sale'),
    ], string='Tipe', default='all', required=True)

    @api.multi
    def print_report(self):
        array_brand = []
        if len(self.brand_ids) == 0:
            self.brand_ids = self.env['product.brand'].search([])
        for brand in self.brand_ids:
            array_brand.append( brand.id )

        groupby_dict = {}

        if self.type == 'all' or self.type == 'sale':
            # SO transaction
            invoices = self.env['account.invoice'].search([
                ('paid_date', '>=', self.start_date),
                ('paid_date', '<=', self.end_date),
                ('state', '=', 'paid'),
                ('type', '=', 'out_invoice'),
            ])

            for invoice in invoices:
                lines = self.env['account.invoice.line'].search([
                    ('product_id.categ_id.is_consigment', '=', False),
                    ('invoice_id', '=', invoice.id),
                    ('product_id.brand_id.id', 'in', array_brand),
                ])
                for line in lines:
                    brand = line.product_id.brand_id.name
                    product = 'SO-' + str(invoice.id) + '-' + str(line.product_id.id) + '-' + str(line.price_unit)

                    total = line.price_unit * line.quantity
                    discount = line.price_subtotal - total
                    
                    if not brand in groupby_dict:
                        groupby_dict[brand] = {}

                    if product in groupby_dict[brand]:
                        groupby_dict[brand][product][3] += line.quantity
                        groupby_dict[brand][product][4] += line.quantity
                        groupby_dict[brand][product][6] += discount
                        groupby_dict[brand][product][7] += line.price_subtotal
                    else:
                        picking = [
                            invoice.origin,         #0
                            invoice.paid_date,      #1
                            line.product_id.name,   #2
                            line.quantity,          #3
                            line.quantity,          #4
                            line.price_unit,        #5
                            discount,               #6
                            line.price_subtotal,    #7
                        ]
                        groupby_dict[brand][product] = picking
                
        if self.type == 'all' or self.type == 'pos':
            # POS transaction
            pos_order_lines = self.env['pos.order.line'].search([
                ('order_id.date_order', '>=', self.start_date),
                ('order_id.date_order', '<=', self.end_date),
                ('product_id.categ_id.is_consigment', '=', False),
                ('product_id.brand_id.id', 'in', array_brand),
            ])

            for line in pos_order_lines:
                brand = line.product_id.brand_id.name
                product = 'POS-' + str(line.order_id.id) + '-' + str(line.product_id.id) + '-' + str(line.price_unit)

                discount = (line.price_unit*line.qty) - line.price_subtotal_incl
                promo = 0

                if not brand in groupby_dict:
                    groupby_dict[brand] = {}
                
                if product in groupby_dict[brand]:
                    groupby_dict[brand][product][3] += line.qty
                    groupby_dict[brand][product][4] += line.qty
                    groupby_dict[brand][product][6] += discount
                    groupby_dict[brand][product][7] += line.price_subtotal
                else:
                    promo_lines = self.env['pos.order.line'].search([
                        ('order_id.id', '=', line.order_id.id),
                        ('product_get_promo_id', '=', line.product_id.id),
                    ])
                    for promo_line in promo_lines:
                        promo += promo_line.price_subtotal_incl
                    
                    discount -= promo
                    picking = [
                        line.order_id.name,                 #0 
                        line.order_id.date_order,           #1
                        line.product_id.name,               #2
                        line.qty,                           #3
                        line.qty,                           #4
                        line.price_unit,                    #5
                        discount,                           #6
                        line.price_subtotal_incl + promo,   #7
                    ]
                    groupby_dict[brand][product] = picking
            
        datas = {
            'ids': self.ids,
            'model': 'report.brand.sales',
            'form': groupby_dict,
            'date': str(self.start_date) + ' sampai ' + str( self.end_date ),
        }
        return self.env['report'].get_action(self, 'report_brand_sales.report_temp', data=datas)