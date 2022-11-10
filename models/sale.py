import logging
from odoo import api, fields, models

_logger = logging.getLogger(__name__)

class SaleReportCustomer(models.TransientModel):
    _name = 'sale.so.report'

    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date(string="End Date", required=True)
    partner_ids = fields.Many2many('res.partner', string="Pelanggan", required=False)

    @api.multi
    def print_so_report_customer(self):
        final_dict = {}
        if len(self.partner_ids) == 0:
            self.partner_ids = self.env['res.partner'].search([
                ('customer', '=', True)
            ], 
            order="name asc")
        for partner in self.partner_ids:
            sale_orders = self.env['sale.order'].search([
                ('date_order', '<=', self.end_date),
                ('date_order', '>=', self.start_date),
                ('state', '=', 'sale'),
                ('invoice_status', '=', 'invoiced'),
                ('partner_id.name', '=', partner.name)
            ],
            order="date_order asc")
            partner_so = []
            for so in sale_orders:
                sale_order = []
                sale_order.append(so.name) #0
                sale_order.append(so.date_order) #1
                sale_order.append(so.user_id.name) #2
                orderline = []
                for ol in so.order_line:
                    so_detail = []
                    so_detail.append(ol.product_id.name) #0
                    so_detail.append(ol.product_uom_qty) #1
                    so_detail.append(ol.product_uom.name) #2
                    so_detail.append(ol.price_unit) #3
                    so_detail.append(ol.tax_id.name) #4
                    so_detail.append(ol.discount) #5
                    so_detail.append(ol.price_subtotal) #6
                    orderline.append(so_detail)
                sale_order.append(orderline) #3
                sale_order.append(so.amount_untaxed) #4
                sale_order.append(so.amount_tax) #5
                sale_order.append(so.price_total_no_discount) #6
                sale_order.append(so.discount_total) #7
                sale_order.append(so.amount_total) #8
                partner_so.append(sale_order)

            final_dict[partner.name] = partner_so

        datas = {
            'ids': self.ids,
            'model': 'sale.so.report',
            'form': final_dict,
            'start_date': self.start_date,
            'end_date': self.end_date,

        }
        return self.env['report'].get_action(self,'so_report_groupby_customer.so_report_groupby_customer', data=datas)
