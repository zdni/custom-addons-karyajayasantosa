from odoo import fields, _

import logging
_logger = logging.getLogger(__name__)

try:
    from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
except ImportError:
    class ReportXlsx(object):
        def __init__(self, *args, **kwargs):
            pass

class ReportInventoryAdjustmentXlsx(ReportXlsx):

    def generate_xlsx_report(self, workbook, data, objects):
        res_filter = {
            'none':  _('All products'),
            'category':  _('One product category'),
            'product':  _('One product only'),
            'partial':  _('Select products manually'),
            'owner':  _('One owner only'), 
            'product_owner':  _('One product for a specific owner'),
            'lot':  _('One Lot/Serial Number'),
            'pack':  _('A Pack')
        }
        res_state = {
            'draft': 'Draft',
            'cancel': 'Cancelled',
            'confirm': 'In Progress',
            'done': 'Validated'
        }
        doc_id = data['form']['id']

        document = self.env['stock.inventory'].search([ ('id', '=', doc_id) ])
        user_currency = self.env.user.company_id.currency_id

        row = col = 0
        format_title = workbook.add_format({'font_size': 22, 'bold': 1, 'align': 'center', 'valign': 'vcenter'})
        format_table_header = workbook.add_format({'font_size': 12, 'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vcenter'})
        format_table_header_right = workbook.add_format({'font_size': 12, 'bold': 1, 'border': 1, 'align': 'right', 'valign': 'vcenter'})
        format_table_cell = workbook.add_format({'font_size': 11, 'border': 1, 'valign': 'vcenter'})
        format_table_cell_bold = workbook.add_format({'font_size': 11, 'bold': 1, 'border': 1, 'valign': 'vcenter'})
        format_table_cell_bold_right = workbook.add_format({'font_size': 11, 'bold': 1, 'border': 1, 'valign': 'vcenter', 'align': 'right'})
        format_table_cell_right = workbook.add_format({'font_size': 11, 'border': 1, 'valign': 'vcenter', 'align': 'right'})

        # title
        worksheet = workbook.add_worksheet("Inventory Adjustment")
        row += 2
        worksheet.merge_range(row, col, row+1, col+6, document.name, format_title)
        row += 3
        
        # information
        worksheet.write(row, col, "Lokasi", format_table_cell_bold)
        worksheet.write(row, col+1, ":", format_table_cell)
        worksheet.write(row, col+2, (document.location_id.location_id.name or '') + ('/' + document.location_id.name), format_table_cell)
        worksheet.write(row+1, col, "Tipe", format_table_cell_bold)
        worksheet.write(row+1, col+1, ":", format_table_cell)
        worksheet.write(row+1, col+2, res_filter[document.filter], format_table_cell)
        worksheet.write(row+2, col, "Terakhir Diperbarui", format_table_cell_bold)
        worksheet.write(row+2, col+1, ":", format_table_cell)
        worksheet.write(row+2, col+2, document.write_uid.name, format_table_cell)

        worksheet.write(row, col+4, "Tanggal", format_table_cell_bold)
        worksheet.write(row, col+5, ":", format_table_cell)
        worksheet.write(row, col+6, document.date, format_table_cell)
        worksheet.write(row+1, col+4, "Tanggal Akuntansi", format_table_cell_bold)
        worksheet.write(row+1, col+5, ":", format_table_cell)
        worksheet.write(row+1, col+6, document.accounting_date, format_table_cell)
        worksheet.write(row+2, col+4, "Status", format_table_cell_bold)
        worksheet.write(row+2, col+5, ":", format_table_cell)
        worksheet.write(row+2, col+6, res_state[document.state], format_table_cell)

        row += 6

        worksheet.write(row, col, "Produk", format_table_header)
        worksheet.write(row, col+1, "UoM", format_table_header)
        worksheet.write(row, col+2, "Kuantitas Sistem", format_table_header)
        worksheet.write(row, col+3, "Kuantitas Nyata", format_table_header)
        worksheet.write(row, col+4, "Selisih", format_table_header)
        worksheet.write(row, col+5, "HPP", format_table_header_right)
        worksheet.write(row, col+6, "Total HPP", format_table_header_right)

        row += 1
        total_hpp = 0
        for line in document.line_ids:
            diff_qty = line.product_qty-line.theoretical_qty
            product = line.product_id
            total_hpp += (product.standard_price*diff_qty)

            worksheet.write(row, col, product.display_name, format_table_cell)
            worksheet.write(row, col+1, line.product_uom_id.name, format_table_cell)
            worksheet.write(row, col+2, line.theoretical_qty, format_table_cell)
            worksheet.write(row, col+3, line.product_qty, format_table_cell)
            worksheet.write(row, col+4, diff_qty, format_table_cell)
            worksheet.write(row, col+5, product.standard_price, format_table_cell_right)
            worksheet.write(row, col+6, product.standard_price*diff_qty, format_table_cell_right)

            row += 1
        
        row += 2
        worksheet.merge_range(row, col, row, col+5, "Total", format_table_cell_bold)
        worksheet.write(row, col+6, total_hpp, format_table_cell_bold_right)

ReportInventoryAdjustmentXlsx('report.report_inv_adj_xlsx', 'stock.inventory')
