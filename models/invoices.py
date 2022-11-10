
from odoo import api, fields, models
import logging


_logger = logging.getLogger(__name__)

class AccountPaidInvoicesReport(models.TransientModel):
    _name = 'account.invoices.paid.report'

    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date(string="End Date", required=True)

    def get_sale_orders(self, invoice_id):
        # sale_orders = self.env['sale.order'].search([ ('invoice_ids', 'in', [invoice_id] ),('date_invoice', '>=', self.start_date), ('date_invoice', '<=', self.end_date),   ])
        sale_orders = self.env['sale.order'].search([ ('invoice_ids', 'in', [invoice_id] ) ])
        filtered_order = list(filter(lambda x: invoice_id in x.invoice_ids , sale_orders))

        return filtered_order[0].name if len( filtered_order ) > 0 else ""

    @api.multi
    def print_vise_report(self):
        invoices = self.env['account.invoice'].search([ ('date_invoice', '>=', self.start_date), ('date_invoice', '<=', self.end_date), ('state', '=', 'paid' ), ('type', '=', 'out_invoice' ) ], order="date_invoice asc")
        invoices_list = [ 
            {
                "number" : item.number,
                "sale_order" : self.get_sale_orders( item ),
                "date_invoice" : item.date_invoice,
                "partner_name" : item.partner_id.name,
                "amount_discount" : sum( ( line.price_unit * line.discount ) for line in item.invoice_line_ids) ,
                "amount_total" : item.amount_total,
            }
            for item in invoices ]
        # _logger.warning( invoices_list )
        datas = {
            'ids': self.ids,
            'model': 'point_of_sale.pos.report',
            'form': invoices_list,
            'start_date': self.start_date,
            'end_date': self.end_date,
        }
        # return
        return self.env['report'].get_action(self,'account_report_paid_invoice.invoice_temp', data=datas)
       