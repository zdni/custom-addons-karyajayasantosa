import re
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

class ProfitPosReportXlsx(ReportXlsx):

    def generate_xlsx_report(self, workbook, data, objects):
        start_date = data['form']['start_date']
        end_date = data['form']['end_date']
        user_ids = self.env['res.users'].browse(data['form']['user_ids'])

        format_main_header = workbook.add_format({'font_size': 18, 'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vcenter'})
        format_table_header = workbook.add_format({'font_size': 12, 'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vcenter'})
        format_table_header_right = workbook.add_format({'font_size': 12, 'bold': 1, 'border': 1, 'align': 'right', 'valign': 'vcenter'})
        format_table_footer = workbook.add_format({'font_size': 11, 'bold': 1, 'border': 1, 'valign': 'vcenter'})
        format_table_cell = workbook.add_format({'font_size': 11, 'border': 1, 'valign': 'vcenter'})
        format_table_cell_bold = workbook.add_format({'font_size': 11, 'bold': 1, 'border': 1, 'valign': 'vcenter'})
        format_table_cell_bold_right = workbook.add_format({'font_size': 11, 'bold': 1, 'border': 1, 'valign': 'vcenter', 'align': 'right'})
        format_table_cell_right = workbook.add_format({'font_size': 11, 'border': 1, 'valign': 'vcenter', 'align': 'right'})
        format_cell = workbook.add_format({'font_size': 11})

        for user in user_ids:
            row = col = 0
            sessions = self.env['pos.session'].search([ 
                ('user_id', '=', user.id), 
                ('start_at', '>=', start_date), 
                ('start_at', '<=', end_date), 
                ('state', '=', 'closed' ) 
            ], order="start_at asc")

            worksheet = workbook.add_worksheet(user.name)
            
            worksheet.merge_range(row, col, row+1, col+1, user.name, format_main_header)
            row += 4

            worksheet.set_column(0, 0, 20)
            worksheet.set_column(1, 1, 20)

            total_sales = 0
            for session in sessions:
                worksheet.merge_range(row, col, row+1, col+1, "SESSION: " + session.name, format_main_header)
                row += 4
                worksheet.write(row, col, "Bank/Cash", format_table_header)
                worksheet.write(row, col+1, "Total", format_table_header_right)
                row += 1
                
                total_sales_per_session = 0
                for statement in session.statement_ids:
                    total_sales += statement.total_entry_encoding
                    total_sales_per_session += statement.total_entry_encoding
                    worksheet.write(row, col, statement.journal_id.name, format_table_cell)
                    worksheet.write(row, col+1, statement.total_entry_encoding, format_table_cell_right)
                    row += 1
                
                worksheet.write(row, col, "Total Transaksi", format_table_cell_bold)
                worksheet.write(row, col+1, total_sales, format_table_cell_bold_right)
                row += 3

            worksheet.write(row, col, "Total Transaksi", format_table_cell_bold)
            worksheet.write(row, col+1, total_sales, format_table_cell_bold_right)


ProfitPosReportXlsx('report.salesperson_pos_xlsx', 'point_of_sale.pos.report')