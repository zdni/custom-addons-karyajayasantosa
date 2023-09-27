from datetime import datetime, date, timedelta

import logging
_logger = logging.getLogger(__name__)

try:
    from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
except ImportError:
    class ReportXlsx(object):
        def __init__(self, *args, **kwargs):
            pass

class ForecastCollectionReportXlsx(ReportXlsx):

    def generate_xlsx_report(self, workbook, data, objects):
        date_end = data['form']['end_date']
        city_ids = data['form']['city_ids']
        today = date.today()

        row = col = 0
        format_table_header = workbook.add_format({'font_size': 12, 'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vcenter'})
        format_table_header_right = workbook.add_format({'font_size': 12, 'bold': 1, 'border': 1, 'align': 'right', 'valign': 'vcenter'})
        format_table_cell = workbook.add_format({'font_size': 11, 'border': 1, 'valign': 'vcenter'})
        format_table_cell_right = workbook.add_format({'font_size': 11, 'border': 1, 'valign': 'vcenter', 'align': 'right'})
        
        if len(city_ids) == 0:
            cities = self.env['vit.kota'].search([])
        else:
            cities = self.env['vit.kota'].search(['id', 'in', city_ids])

        datas = {}
        for city in cities:
            customers = self.env['res.partner'].search([('kota_id.id', '=', city.id)])
            customer_data = []
            for customer in customers:
                customer_invoices = []
                invoices = self.env['account.invoice'].search([
                    ('partner_id', '=', customer.id),
                    ('state', 'in', ['open']),
                    ('type', '=', 'out_invoice'),
                    ('date_due', '<=', date_end),
                ], order='date_invoice asc')
                for invoice in invoices:
                    date_invoice = datetime.strptime(invoice.date_invoice, '%Y-%m-%d').date()
                    due_date = date_invoice + timedelta(days=(customer.due_date_customer-1))
                    invoice_age = today - date_invoice
                    
                    if due_date <= datetime.strptime(date_end, '%Y-%m-%d').date():
                        bg_number = '-'
                        giros = self.env['vit.giro'].search([ ('giro_invoice_ids.invoice_id', '=', invoice.id) ])
                        if giros:
                            for giro in giros:
                                bg_number = bg_number + ' ' + giro.name

                        data = {
                            'invoice': invoice.number,
                            'payment_term': str(customer.due_date_customer) + ' Hari',
                            'invoice_age': str(invoice_age.days+1) + ' Hari',
                            'customer': customer.display_name,
                            'credit_limit': customer.credit_limit,
                            'date_invoice': datetime.strptime(invoice.date_invoice, '%Y-%m-%d').strftime('%d/%m/%Y'),
                            'sales': invoice.user_id.name,
                            'date_due': due_date.strftime('%d/%m/%Y'),
                            'giro': bg_number,
                            'amount_total': invoice.amount_total,
                            'residual': invoice.residual
                        }

                        customer_invoices.append(data)
                if len(customer_invoices) > 0: customer_data.append(customer_invoices)
        
            if len(customer_data) > 0: datas[city.name] = customer_data

        worksheet = workbook.add_worksheet("LAPORAN PERKIRAAN TAGIHAN")
        worksheet.merge_range(row, col, row + 1, col+10, "LAPORAN PERKIRAAN TAGIHAN", format_table_header)
        
        row += 2
        date_string = 'Sampai Tanggal ' + datetime.strptime(date_end, "%Y-%m-%d").strftime("%d %B %Y")
        worksheet.merge_range(row, col, row, col+10, date_string, format_table_header)
        row += 1
        worksheet.merge_range(row, col, row, col+10, ("*Catatan : Umur Piutang Per Tanggal " + datetime.now().strftime("%d %B %Y")), format_table_header)
        row += 2

        for city in datas.keys():
            row += 1
            worksheet.merge_range(row, col, row, col+10, city, format_table_header)
            row += 1

            worksheet.write(row, col, 'Tagihan', format_table_header)
            worksheet.write(row, col+1, 'Payment Term', format_table_header)
            worksheet.write(row, col+2, 'Umur Piutang', format_table_header)
            worksheet.write(row, col+3, 'Pelanggan', format_table_header)
            worksheet.write(row, col+4, 'Kredit Limit', format_table_header)
            worksheet.write(row, col+5, 'Tgl Tagihan', format_table_header)
            worksheet.write(row, col+6, 'Tgl Jatuh Tempo', format_table_header)
            worksheet.write(row, col+7, 'Giro', format_table_header)
            worksheet.write(row, col+8, 'Sales', format_table_header)
            worksheet.write(row, col+9, 'Total Tagihan (Rp)', format_table_header_right)
            worksheet.write(row, col+10, 'Sisa Tagihan (Rp)', format_table_header_right)
            row += 1
            
            for invoices in datas[city]:
                for invoice in invoices:
                    worksheet.write(row, col, invoice['invoice'], format_table_cell)
                    worksheet.write(row, col+1, invoice['payment_term'], format_table_cell)
                    worksheet.write(row, col+2, invoice['invoice_age'], format_table_cell)
                    worksheet.write(row, col+3, invoice['customer'], format_table_cell)
                    worksheet.write(row, col+4, invoice['credit_limit'], format_table_cell)
                    worksheet.write(row, col+5, invoice['date_invoice'], format_table_cell)
                    worksheet.write(row, col+6, invoice['date_due'], format_table_cell)
                    worksheet.write(row, col+7, invoice['giro'], format_table_cell)
                    worksheet.write(row, col+8, invoice['sales'], format_table_cell)
                    worksheet.write(row, col+9, invoice['amount_total'], format_table_cell_right)
                    worksheet.write(row, col+10, invoice['residual'], format_table_cell_right)
                    row += 1



ForecastCollectionReportXlsx('report.forecast_collection_report_xlsx', 'forecast.collection.report')
