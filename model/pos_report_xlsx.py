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
        type_report = data['form']['type_report']
        row_recap_ws = col_recap_ws = 0

        format_main_header = workbook.add_format({'font_size': 18, 'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vcenter'})
        format_table_header = workbook.add_format({'font_size': 12, 'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vcenter'})
        format_table_header_right = workbook.add_format({'font_size': 12, 'bold': 1, 'border': 1, 'align': 'right', 'valign': 'vcenter'})
        format_table_footer = workbook.add_format({'font_size': 11, 'bold': 1, 'border': 1, 'valign': 'vcenter'})
        format_table_cell = workbook.add_format({'font_size': 11, 'border': 1, 'valign': 'vcenter'})
        format_table_cell_bold = workbook.add_format({'font_size': 11, 'bold': 1, 'border': 1, 'valign': 'vcenter'})
        format_table_cell_right = workbook.add_format({'font_size': 11, 'border': 1, 'valign': 'vcenter', 'align': 'right'})
        format_cell_bold = workbook.add_format({'font_size': 11})

        # ---------------------Project details-------------------------- #
        sessions = self.env['pos.session'].search([ 
            ('stop_at', '<=', data['form']['end_date']),
            ('stop_at', '>=', data['form']['start_date']),
            ('state', '=', 'closed'),
        ], order="stop_at asc")

        # RECAP SESSION
        recap_ws = workbook.add_worksheet('Rekap Session')
        recap_ws.merge_range(row_recap_ws, col_recap_ws, row_recap_ws + 1, col_recap_ws + 2, "LAPORAN PROFIT POS", format_main_header)
        
        # ----------------------Header Tabel---------------------- #
        recap_ws.set_column(0, 0, 20)    #set A column width
        recap_ws.set_column(1, 1, 15)    #set B column width
        recap_ws.set_column(2, 2, 20)    #set C column width
        row_recap_ws += 4

        recap_total_trans = recap_hpp = recap_margin = 0
        for session in sessions:

            if type_report == 'detail':
                name = re.sub("/", '-', session.name)
                session_ws = workbook.add_worksheet(name)
                row_session_ws = col_session_ws = 0
                session_ws.merge_range(row_session_ws, col_session_ws, row_session_ws + 1, col_session_ws + 6, "DETAIL PROFIT POS", format_main_header)
                row_session_ws += 4

            transactions = self.env['pos.order'].search([
                ('session_id', '=', session.name),
                ('state', '=', 'done'),
            ])

            total_hpp_transaction = 0
            for transaction in transactions:
                # check if return transaction or not
                order = self.env['pos.order'].search([
                    ('pos_reference', '=', transaction.pos_reference)
                ], order="date_order asc, id asc", limit =1)
                is_return = True if transaction.id != order.id else False
                
                if type_report == 'detail':
                    session_ws.merge_range(row_session_ws, col_session_ws, row_session_ws, col_session_ws+6, transaction.name, format_cell_bold)
                    row_session_ws += 1
                
                    session_ws.write(row_session_ws, col_session_ws, "Produk", format_table_header)
                    session_ws.set_column(0, 0, 70)    #set A column width
                    session_ws.write(row_session_ws, col_session_ws+1, "UoM", format_table_header)
                    session_ws.set_column(1, 1, 10)    #set A column width
                    session_ws.write(row_session_ws, col_session_ws+2, "Qty", format_table_header_right)
                    session_ws.write(row_session_ws, col_session_ws+3, "Diskon", format_table_header_right)
                    session_ws.set_column(3, 3, 20)    #set A column width
                    session_ws.write(row_session_ws, col_session_ws+4, "Subtotal", format_table_header_right)
                    session_ws.set_column(4, 4, 20)    #set A column width
                    session_ws.write(row_session_ws, col_session_ws+5, "HPP", format_table_header_right)
                    session_ws.set_column(5, 5, 20)    #set A column width
                    session_ws.write(row_session_ws, col_session_ws+6, "Margin", format_table_header_right)
                    session_ws.set_column(6, 6, 20)    #set A column width
                    row_session_ws += 1

                total_hpp_product = index = j = 0
                for line in transaction.lines:
                    if index < len(transaction.lines):
                        if not line.product_id.categ_id.is_consigment:
                            hpp_product = 0
                            if line.product_id.type == 'product':
                                if is_return:
                                    find = False
                                    while not find:
                                        if j >= len(order.lines) or j >= len(order.picking_id.move_lines):
                                            break
                                        product_id = order.lines[j].product_id.id
                                        if product_id == line.product_id.id:
                                            find = True
                                            move_line = order.picking_id.move_lines[j]
                                            for quant_line in move_line.quant_ids:
                                                hpp_product += quant_line.inventory_value
                                            hpp_product = hpp_product*-1
                                        j += 1
                                else:
                                    find = False
                                    while not find:
                                        if index >= len(transaction.picking_id.move_lines):
                                            break
                                        if transaction.picking_id.move_lines[index].product_id.id != line.product_id.id:
                                            index += 1
                                        else:
                                            find = True
                                            move_line = transaction.picking_id.move_lines[index]
                                            for quant_line in move_line.quant_ids:
                                                hpp_product += quant_line.inventory_value

                                index += 1

                            if line.product_get_promo_id and line.product_get_promo_id.categ_id and line.product_get_promo_id.categ_id.is_consigment:
                                continue
                            if line.category_get_promo_id and line.category_get_promo_id.is_consigment:
                                continue

                            margin_product = line.price_subtotal_incl - hpp_product
                            total_hpp_product += hpp_product

                            if type_report == 'detail':
                                session_ws.write(row_session_ws, col_session_ws, line.product_id.name, format_table_cell)
                                session_ws.write(row_session_ws, col_session_ws+1, line.product_id.uom_id.name, format_table_cell)
                                session_ws.write(row_session_ws, col_session_ws+2, line.qty, format_table_cell_right)
                                session_ws.write(row_session_ws, col_session_ws+3, line.discount, format_table_cell_right)
                                session_ws.write(row_session_ws, col_session_ws+4, line.price_subtotal_incl, format_table_cell_right)
                                session_ws.write(row_session_ws, col_session_ws+5, hpp_product, format_table_cell_right)
                                session_ws.write(row_session_ws, col_session_ws+6, margin_product, format_table_cell_right)
                                row_session_ws += 1
                
                total_hpp_transaction += total_hpp_product
                amount_total = transaction.amount_total
                margin_transaction = amount_total - total_hpp_product

                if type_report == 'detail':
                    session_ws.merge_range(row_session_ws, col_session_ws, row_session_ws, col_session_ws+3, "Total", format_table_cell_bold)
                    session_ws.write(row_session_ws, col_session_ws+4, amount_total, format_table_cell_right)
                    session_ws.write(row_session_ws, col_session_ws+5, total_hpp_product, format_table_cell_right)
                    session_ws.write(row_session_ws, col_session_ws+6, margin_transaction, format_table_cell_right)
                    row_session_ws += 2

            
            
            
            
            
            recap_ws.write(row_recap_ws, col_recap_ws,   "POS SESSION", format_table_header)
            recap_ws.write(row_recap_ws, col_recap_ws+1, "KASIR",     format_table_header)
            recap_ws.write(row_recap_ws, col_recap_ws+2, "TGL SESSION",   format_table_header)

            row_recap_ws += 1
            recap_ws.write(row_recap_ws, col_recap_ws, session.name, format_table_cell)
            recap_ws.write(row_recap_ws, col_recap_ws+1, session.user_id.name, format_table_cell)
            recap_ws.write(row_recap_ws, col_recap_ws+2, session.stop_at, format_table_cell)
            
            row_recap_ws += 2
            recap_ws.merge_range(row_recap_ws, col_recap_ws, row_recap_ws, col_recap_ws+1, "BANK", format_table_header)
            recap_ws.write(row_recap_ws, col_recap_ws+2, "SALDO AKHIR",     format_table_header)
            
            row_recap_ws += 1
            total_trans = margin = 0
            hpp = total_hpp_transaction
            recap_hpp += total_hpp_transaction
            for statement in session.statement_ids:
                recap_ws.merge_range(row_recap_ws, col_recap_ws, row_recap_ws, col_recap_ws+1, statement.journal_id.name, format_table_cell)
                recap_ws.write(row_recap_ws, col_recap_ws+2, statement.total_entry_encoding, format_table_cell)
                
                total_trans += statement.total_entry_encoding
                recap_total_trans += statement.total_entry_encoding

                row_recap_ws += 1

            recap_ws.merge_range(row_recap_ws, col_recap_ws, row_recap_ws, col_recap_ws+1, "TOTAL TRANSAKSI", format_table_footer)
            recap_ws.write(row_recap_ws, col_recap_ws+2, total_trans, format_table_footer)
            
            row_recap_ws += 1
            recap_ws.merge_range(row_recap_ws, col_recap_ws, row_recap_ws, col_recap_ws+1, "HPP", format_table_footer)
            recap_ws.write(row_recap_ws, col_recap_ws+2, hpp, format_table_footer)
            
            row_recap_ws += 1
            margin = total_trans - hpp
            recap_ws.merge_range(row_recap_ws, col_recap_ws, row_recap_ws, col_recap_ws+1, "MARGIN", format_table_footer)
            recap_ws.write(row_recap_ws, col_recap_ws+2, margin, format_table_footer)

            row_recap_ws += 4

        recap_ws.merge_range(row_recap_ws, col_recap_ws, row_recap_ws + 1, col_recap_ws + 2, "REKAP POS SESSION", format_main_header)
        row_recap_ws += 2

        recap_ws.merge_range(row_recap_ws, col_recap_ws, row_recap_ws, col_recap_ws+1, "TOTAL TRANSAKSI", format_table_footer)
        recap_ws.write(row_recap_ws, col_recap_ws+2, recap_total_trans, format_table_footer)
        
        row_recap_ws += 1
        recap_ws.merge_range(row_recap_ws, col_recap_ws, row_recap_ws, col_recap_ws+1, "HPP", format_table_footer)
        recap_ws.write(row_recap_ws, col_recap_ws+2, recap_hpp, format_table_footer)
        
        row_recap_ws += 1
        recap_margin = recap_total_trans - recap_hpp
        recap_ws.merge_range(row_recap_ws, col_recap_ws, row_recap_ws, col_recap_ws+1, "MARGIN", format_table_footer)
        recap_ws.write(row_recap_ws, col_recap_ws+2, recap_margin, format_table_footer)


ProfitPosReportXlsx('report.profit_pos_report_xlsx', 'pos.report')
