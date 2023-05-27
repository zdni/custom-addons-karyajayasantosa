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
        invoices = self.env['account.invoice'].search([
            ('paid_date', '>=', self.start_date),
            ('paid_date', '<=', self.end_date),
            ('state', '=', 'paid'),
            ('type', '=', 'out_invoice'),
        ])

        for invoice in invoices:
            operations = self.env['stock.pack.operation'].search([
                ('product_id.categ_id.is_consigment', '=', False),
                ('picking_id.origin', '=', invoice.origin),
                ('product_id.brand_id.id', 'in', array_brand),
            ])

            for operation in operations:
                picking = []
                qty_invoiced = operation.product_qty

                picking.append( invoice.origin )
                picking.append( invoice.paid_date )
                picking.append( operation.product_id.name )
                picking.append( operation.product_qty )

                invoice_line = self.env['account.invoice.line'].search([
                    ('product_id.id', '=', operation.product_id.id),
                    ('quantity', '=', operation.product_qty),
                    ('invoice_id.id', '=', invoice.id),
                ], limit=1)
                if len( invoice_line ) < 1:
                    invoice_line = self.env['account.invoice.line'].search([
                        ('product_id.id', '=', operation.product_id.id),
                        ('invoice_id.id', '=', invoice.id),
                    ], limit=1)

                    so_line = self.env['sale.order.line'].search([
                        ('product_id.id', '=', operation.product_id.id),
                        ('order_id.name', '=', invoice.origin),
                    ], limit=1)
                    qty_invoiced = so_line.qty_invoiced 

                total = invoice_line.price_unit * qty_invoiced
                discount = invoice_line.price_subtotal - total

                picking.append( qty_invoiced )
                picking.append( invoice_line.price_unit )
                picking.append( discount )
                picking.append( invoice_line.price_subtotal )

                brand = operation.product_id.brand_id.name
                if brand in groupby_dict:
                    groupby_dict[brand].append( picking )
                else:
                    groupby_dict[brand] = [picking]

        # POS transaction
        pos_order_lines = self.env['pos.order.line'].search([
            ('order_id.date_order', '>=', self.start_date),
            ('order_id.date_order', '<=', self.end_date),
            ('product_id.categ_id.is_consigment', '=', False),
            ('product_id.brand_id.id', 'in', array_brand),
        ])

        for line in pos_order_lines:
            name = line.order_id.name
            operations = self.env['stock.pack.operation'].search([
                ('product_id.id', '=', line.product_id.id),
                ('picking_id.origin', '=', name)
            ], limit=1)
            for operation in operations:
                picking = []

                discount = (line.price_unit*operation.product_qty) - line.price_subtotal_incl
                promo_lines = self.env['pos.order.line'].search([
                    ('order_id.id', '=', line.order_id.id),
                    ('product_get_promo_id', '=', line.product_id.id),
                ])
                promo = 0
                for promo_line in promo_lines:
                    promo += promo_line.price_subtotal_incl

                discount -= promo

                picking.append( name )
                picking.append( line.order_id.date_order )
                picking.append( operation.product_id.name )
                picking.append( operation.product_qty )
                picking.append( operation.product_qty )
                picking.append( line.price_unit )
                picking.append( discount )
                picking.append( line.price_subtotal_incl + promo )

                brand = line.product_id.brand_id.name
                
                if brand in groupby_dict:
                    groupby_dict[brand].append( picking )
                else:
                    groupby_dict[brand] = [picking]

        datas = {
            'ids': self.ids,
            'model': 'report.brand.sales',
            'form': groupby_dict,
            'date': str(self.start_date) + ' sampai ' + str( self.end_date ),
        }
        return self.env['report'].get_action(self, 'report_brand_sales.report_temp', data=datas)