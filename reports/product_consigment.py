from odoo import api, fields, models, exceptions, _
from datetime import date, datetime, timedelta

import logging
_logger = logging.getLogger(__name__)

class ReportProductConsigment(models.TransientModel):
    _name = "report.product.consigment"

    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date('End Date', required=True)
    brand_ids = fields.Many2many('product.brand', string='Brand')
    vendor_ids = fields.Many2many('res.partner', string='Vendor')

    @api.multi
    def print_report(self):
        ResPartner = self.env['res.partner']
        array_cat_cons = []
        category_consigment = self.env['product.category'].search([('is_consigment', '=', True)])
        for category in category_consigment:
            array_cat_cons.append( category.id )

        array_brand = []
        if len(self.brand_ids) == 0:
            self.brand_ids = self.env['product.brand'].search([])
        for brand in self.brand_ids:
            array_brand.append( brand.id )

        array_vendor = []
        if len(self.vendor_ids) == 0:
            self.vendor_ids = ResPartner.search([('supplier', '=', True)])
        for vendor in self.vendor_ids:
            partners = ResPartner.search([('name', '=', vendor.name)])
            for partner in partners:
                array_vendor.append( partner.id )

        groupby_dict = {}

        # SO transaction
        query = """
            SELECT mail_message.id AS mail_message_id, 
                mail_message.res_id AS mail_message_res_id, 
                mail_message.create_date, 
                account_invoice.origin, 
                account_invoice.date_invoice, 
                account_invoice.number, 
                account_invoice_line.product_id
            FROM account_invoice
            JOIN mail_message ON mail_message.res_id = account_invoice.id
            JOIN account_invoice_line ON account_invoice_line.invoice_id = account_invoice.id
            WHERE account_invoice.state = 'paid'
            AND mail_message.id IN (SELECT MAX(mail_message.id) FROM mail_message WHERE mail_message.subtype_id = 4 GROUP BY mail_message.res_id)
            AND date_invoice <= %s
            AND date_invoice >= %s
            AND mail_message.create_date <= %s
            AND mail_message.create_date >= %s
            AND account_invoice.type = 'out_invoice'
            AND mail_message.subtype_id = 4
            ORDER BY mail_message.create_date
        """
        params = [ self.end_date, self.start_date, self.end_date + ' 23:59:59', self.start_date ]
        
        self.env.cr.execute( query, params )
        invoices = self.env.cr.dictfetchall()

        for invoice in invoices:
            date_paid = self.env['mail.message'].search([
                ('subtype_id', '=', 4),
                ('res_id', '=', invoice['mail_message_res_id'])
            ], limit=1, order='id DESC')
            if date_paid.create_date == invoice['create_date'][:19]:
                origin = invoice['origin']

                operations = self.env['stock.pack.operation'].search([
                    ('owner_id.id', 'in', array_vendor),
                    ('picking_id.origin', '=', origin),
                    ('product_id.categ_id.id', 'in', array_cat_cons),
                    ('product_id.brand_id.id', 'in', array_brand),
                ])

                for line in operations:
                    picking = []

                    picking.append( origin )
                    picking.append( invoice['create_date'] )
                    picking.append( line.product_id.name )
                    picking.append( line.product_qty )

                    invoice_line = self.env['account.invoice.line'].search([
                        ('product_id.id', '=', line.product_id.id),
                        ('quantity', '=', line.product_qty),
                        ('invoice_id.origin', '=', origin),
                    ], limit=1)

                    picking.append(invoice_line.price_unit)
                    picking.append(invoice_line.price_subtotal)

                    brand = line.product_id.brand_id.name
                    vendor = line.owner_id.display_name

                    if vendor in groupby_dict:
                        if brand in groupby_dict[vendor]:
                            groupby_dict[vendor][brand].append( picking )
                        else:
                            groupby_dict[vendor][brand] = [picking]
                    else:
                        groupby_dict[vendor] = {}
                        groupby_dict[vendor][brand] = [picking]

        
        # POS transaction
        pos_order_lines = self.env['pos.order.line'].search([
            ('order_id.date_order', '>=', self.start_date),
            ('order_id.date_order', '<=', self.end_date),
            ('product_id.categ_id.id', 'in', array_cat_cons),
            ('product_id.brand_id.id', 'in', array_brand),
        ])

        for line in pos_order_lines:
            name = line.order_id.name
            operations = self.env['stock.pack.operation'].search([
                ('product_id.id', '=', line.product_id.id),
                ('owner_id.id', 'in', array_vendor),
                ('picking_id.origin', '=', name)
            ])
            for operation in operations:
                picking = []

                picking.append( name )
                picking.append( line.order_id.date_order )
                picking.append( operation.product_id.name )
                picking.append( operation.product_qty )
                picking.append( line.price_unit )
                picking.append( line.price_subtotal_incl )

                brand = operation.product_id.brand_id.name
                vendor = operation.owner_id.display_name

                if vendor in groupby_dict:
                    if brand in groupby_dict[vendor]:
                        groupby_dict[vendor][brand].append( picking )
                    else:
                        groupby_dict[vendor][brand] = [picking]
                else:
                    groupby_dict[vendor] = {}
                    groupby_dict[vendor][brand] = [picking]
        
        datas = {
            'ids': self.ids,
            'model': 'report.product.consigment',
            'form': groupby_dict,
            'date': str(self.start_date) + ' sampai ' + str( self.end_date ),
        }
        return self.env['report'].get_action(self, 'report_product_consigment.report_temp', data=datas)