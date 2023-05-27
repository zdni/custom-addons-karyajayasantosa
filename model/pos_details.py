from odoo import fields
from datetime import datetime, date, timedelta
from odoo.exceptions import except_orm
from dateutil.relativedelta import relativedelta

import logging
_logger = logging.getLogger(__name__)

try:
    from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
except ImportError:
    class ReportXlsx(object):
        def __init__(self, *args, **kwargs):
            pass

class PosDetailsReportXlsx(ReportXlsx):

    def generate_xlsx_report(self, workbook, data, objects):
        date_start = data['form']['start_date']
        date_end = data['form']['end_date']
        configs = self.env['pos.config'].browse(data['form']['pos_config_ids'])

        row = col = 0
        format_table_header = workbook.add_format({'font_size': 12, 'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vcenter'})
        format_table_header_right = workbook.add_format({'font_size': 12, 'bold': 1, 'border': 1, 'align': 'right', 'valign': 'vcenter'})
        format_table_cell = workbook.add_format({'font_size': 11, 'border': 1, 'valign': 'vcenter'})
        format_table_cell_bold = workbook.add_format({'font_size': 11, 'bold': 1, 'border': 1, 'valign': 'vcenter'})
        format_table_cell_right = workbook.add_format({'font_size': 11, 'border': 1, 'valign': 'vcenter', 'align': 'right'})


        worksheet = workbook.add_worksheet("POS DETAILS")
        worksheet.merge_range(row, col, row + 1, col+2, "LAPORAN DETAIL POS", format_table_header)
        row += 2
        
        date_string = date_start + ' sampai ' + date_end
        worksheet.merge_range(row, col, row, col+2, date_string, format_table_header)

        worksheet.set_column(0, 0, 70)
        worksheet.set_column(1, 1, 15)
        worksheet.set_column(2, 2, 20)
        row += 4

        if not configs:
            configs = self.env['pos.config'].search([])

        orders = self.env['pos.order'].search([
            ('date_order', '>=', date_start),
            ('date_order', '<=', date_end),
            ('state', 'in', ['paid','invoiced','done']),
            ('config_id', 'in', configs.ids)])
        user_currency = self.env.user.company_id.currency_id

        total = 0.0
        products_sold = {}
        taxes = {}
        for order in orders:
            if user_currency != order.pricelist_id.currency_id:
                total += order.pricelist_id.currency_id.compute(order.amount_total, user_currency)
            else:
                total += order.amount_total
            currency = order.session_id.currency_id

            for line in order.lines:
                key = (line.product_id, line.price_unit, line.discount)
                products_sold.setdefault(key, 0.0)
                products_sold[key] += line.qty

                if line.tax_ids_after_fiscal_position:
                    line_taxes = line.tax_ids_after_fiscal_position.compute_all(line.price_unit * (1-(line.discount or 0.0)/100.0), currency, line.qty, product=line.product_id, partner=line.order_id.partner_id or False)
                    for tax in line_taxes['taxes']:
                        taxes.setdefault(tax['id'], {'name': tax['name'], 'total':0.0})
                        taxes[tax['id']]['total'] += tax['amount']

        worksheet.write(row, col, "Produk", format_table_header)
        worksheet.write(row, col+1, "Qty", format_table_header_right)
        worksheet.write(row, col+2, "Harga Satuan", format_table_header_right)
        row += 1

        for (product, price_unit, discount), qty in products_sold.items():
            code = "[" + product.default_code + "] " if product.default_code else ''
            product_name = code + str(product.name)
            qty_uom = str(qty) + " " + str(product.uom_id.name)
            
            worksheet.write(row, col, product_name, format_table_cell)
            worksheet.write(row, col+1, qty_uom, format_table_cell_right)
            worksheet.write(row, col+2, price_unit, format_table_cell_right)
            row += 1

        row += 2
        worksheet.merge_range(row, col, row, col+2, "METODE PEMBAYARAN", format_table_header)
        row += 1
        worksheet.write(row, col, "Nama", format_table_cell_bold)
        worksheet.merge_range(row, col+1, row, col+2, "Total", format_table_cell_right)
        row += 1
        
        st_line_ids = self.env["account.bank.statement.line"].search([('pos_statement_id', 'in', orders.ids)]).ids
        if st_line_ids:
            self.env.cr.execute("""
                SELECT aj.name, sum(amount) total
                FROM account_bank_statement_line AS absl,
                     account_bank_statement AS abs,
                     account_journal AS aj 
                WHERE absl.statement_id = abs.id
                    AND abs.journal_id = aj.id 
                    AND absl.id IN %s 
                GROUP BY aj.name
            """, (tuple(st_line_ids),))
            payments = self.env.cr.dictfetchall()
            for payment in payments:
                worksheet.write(row, col, payment['name'], format_table_cell)
                worksheet.merge_range(row, col+1, row, col+2, payment['total'], format_table_cell_right)
                row += 1

        row += 2
        worksheet.merge_range(row, col, row, col+2, "PAJAK", format_table_header)
        row += 1
        worksheet.write(row, col, "Nama", format_table_cell_bold)
        worksheet.merge_range(row, col+1, row, col+2, "Total", format_table_cell_right)
        for tax in taxes:
            worksheet.write(row, col, tax['name'], format_table_cell)
            worksheet.merge_range(row, col+1, row, col+2, tax['total'], format_table_cell_right)
            row += 1

        row += 3
        worksheet.write(row, col, "Total", format_table_cell_bold)
        worksheet.merge_range(row, col+1, row, col+2, user_currency.round(total), format_table_cell_right)


PosDetailsReportXlsx('report.pos_details_report_xlsx', 'pos.details.wizard')
