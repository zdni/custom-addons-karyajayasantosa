from odoo import api, fields, models, _

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
        invoices = self.env['account.invoice'].search([
            ('paid_date', '>=', self.start_date),
            ('paid_date', '<=', self.end_date),
            ('state', '=', 'paid'),
        ])

        for invoice in invoices:
            operations = self.env['stock.pack.operation'].search([
                ('owner_id.id', 'in', array_vendor),
                ('picking_id.origin', '=', invoice.origin),
                ('product_id.categ_id.id', 'in', array_cat_cons),
                ('product_id.brand_id.id', 'in', array_brand),
            ])

            for line in operations:
                picking = []

                picking.append( invoice.origin )
                picking.append( invoice.paid_date )
                picking.append( line.product_id.name )
                picking.append( line.product_qty )

                invoice_line = self.env['account.invoice.line'].search([
                    ('product_id.id', '=', line.product_id.id),
                    ('quantity', '=', line.product_qty),
                    ('invoice_id.id', '=', invoice.id),
                ], limit=1)

                total = invoice_line.price_unit * line.product_qty
                discount = invoice_line.price_subtotal - total

                picking.append( invoice_line.price_unit )
                picking.append( discount )
                picking.append( invoice_line.price_subtotal )

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
        ], order="order_id asc, product_id asc")

        for index, line in enumerate(pos_order_lines):
            discount = line.price_unit*line.qty - line.price_subtotal_incl
            price_subtotal_incl = line.price_subtotal_incl
            price_unit = line.price_unit

            if index > 1:
                prev_line = pos_order_lines[index-1]
                if prev_line.product_id.id == line.product_id.id:
                    continue
            
            if index < len(pos_order_lines)-1:
                idx = 1
                while True:
                    next_line = pos_order_lines[index+idx]
                    if next_line.product_id.id != line.product_id.id:
                        break

                    discount += ( next_line.price_unit*next_line.qty - next_line.price_subtotal_incl )
                    price_subtotal_incl += next_line.price_subtotal_incl
                    price_unit += next_line.price_unit
                    idx += 1
            
            price_unit = price_unit/idx
            
            # pass return order
            return_order = self.env['pos.order'].search([
                ('pos_reference', '=', line.order_id.pos_reference)
            ])
            if len(return_order) > 1:
                continue
            
            name = line.order_id.name
            operations = self.env['stock.pack.operation'].search([
                ('product_id.id', '=', line.product_id.id),
                ('owner_id.id', 'in', array_vendor),
                ('picking_id.origin', '=', name)
            ])
            for operation in operations:
                picking = []

                # discount = (line.price_unit*operation.product_qty) - price_subtotal_incl
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
                picking.append( price_unit )
                picking.append( discount )
                picking.append( price_subtotal_incl + promo )

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