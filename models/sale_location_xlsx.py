from odoo import fields, _
from datetime import datetime, timedelta

import logging
_logger = logging.getLogger(__name__)

try:
    from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
except ImportError:
    class ReportXlsx(object):
        def __init__(self, *args, **kwargs):
            pass

class ReportSaleLocationXlsx(ReportXlsx):

    def generate_xlsx_report(self, workbook, data, objects):
        form = data['form']

        # customer locations
        customer_loc_arr = []
        locations = self.env['stock.location'].search([ ('usage', '=', 'customer') ])
        for location in locations:
            customer_loc_arr.append(location.id)
        
        
        condition_loc = [ ('usage', '=', 'internal'), ('name', '=', 'Stock') ] if len(form['location_ids']) == 0 else [ ('id', 'in', form['location_ids']) ]
        locations = self.env['stock.location'].search(condition_loc)
        
        start_date = datetime.strptime(form['start_date'], '%Y-%m-%d')
        start_date_str = ( start_date + timedelta( days=1, seconds=-1 ) ).strftime("%Y-%m-%d %H:%M:%S")
        end_date = datetime.strptime(form['end_date'], '%Y-%m-%d')
        end_date_str = ( end_date + timedelta( days=1, seconds=-1 ) ).strftime("%Y-%m-%d %H:%M:%S")

        row = col = 0
        format_title = workbook.add_format({'font_size': 22, 'bold': 1, 'align': 'center', 'valign': 'vcenter'})
        format_table_header = workbook.add_format({'font_size': 12, 'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vcenter'})
        format_table_cell = workbook.add_format({'font_size': 11, 'border': 1, 'valign': 'vcenter'})
        format_cell_bold = workbook.add_format({'font_size': 12, 'bold': 1, 'valign': 'vcenter'})
        format_cell_bold_center = workbook.add_format({'font_size': 12, 'bold': 1, 'valign': 'vcenter', 'align': 'center'})

        # title
        worksheet = workbook.add_worksheet("Penjualan per Lokasi")
        row += 2
        worksheet.merge_range(row, col, row+1, col+3+(2*len(locations)), 'Penjualan per Lokasi', format_title)
        row += 2
        worksheet.merge_range(row, col, row, col+3+(2*len(locations)), 'Tanggal Penarikan ' + str(form['end_date']) + ' sampai ' + str(form['start_date']), format_cell_bold_center)
        row += 3
        
        worksheet.merge_range(row, col, row+1, col, "Barcode", format_table_header)
        worksheet.merge_range(row, col+1, row+1, col+1, "Nama Produk", format_table_header)
        worksheet.merge_range(row, col+2, row+1, col+2, "Brand", format_table_header)
        worksheet.merge_range(row, col+3, row+1, col+3, "UoM", format_table_header)
        index = 0
        total_amount_loc = {}
        for location in locations:
            total_amount_loc[location.id] = 0
            loc_name = location.location_id.name + '/' + location.name

            worksheet.merge_range(row, col+4+index, row, col+5+index, loc_name, format_table_header)
            worksheet.write(row+1, col+4+index, 'Qty', format_table_header)
            worksheet.write(row+1, col+5+index, 'Amount (Rp)', format_table_header)
            index += 2
        worksheet.write(row+1, col+4+index, 'Qty', format_table_header)
        worksheet.write(row+1, col+5+index, 'Amount (Rp)', format_table_header)

        row += 2
        if form['type'] == 'product':
            condition_prod = [ ('type', '=', 'product'), ('active', '=', True) ] if len(form['product_ids']) == 0 else [ ('id', 'in', form['product_ids']), ('active', '=', True) ]
            products = self.env['product.product'].search(condition_prod)
            for product in products:
                total_qty = total_amount = 0
                worksheet.write(row, col, product.barcode, format_table_cell)
                worksheet.write(row, col+1, product.name, format_table_cell)
                worksheet.write(row, col+2, product.brand_id.name, format_table_cell)
                worksheet.write(row, col+3, product.uom_id.name, format_table_cell)
                index = 0
                for location in locations:
                    qty = amount = 0
                    move = self.env['stock.move'].search([
                        ('product_id.id', '=', product.id),
                        ('location_id.id', '=', location.id),
                        ('location_dest_id.id', 'in', customer_loc_arr),
                        ('date', '>=', start_date_str),
                        ('date', '<=', end_date_str),
                    ])
                    for line in move: 
                        qty += line.product_uom_qty
                        for quant in line.quant_ids:
                            amount += quant.inventory_value
                    worksheet.write(row, col+4+index, qty, format_table_cell)
                    worksheet.write(row, col+5+index, amount, format_table_cell)
                    
                    total_qty += qty
                    total_amount += amount
                    total_amount_loc[location.id] += amount

                    index += 2
                worksheet.write(row, col+4+index, total_qty, format_table_cell)
                worksheet.write(row, col+5+index, total_amount, format_table_cell)
                row += 1
        
        if form['type'] == 'category':
            condition_cat = [] if len(form['category_ids']) == 0 else [ ('id', 'in', form['category_ids']) ]
            categories = self.env['product.category'].search(condition_cat)
            for category in categories:
                products = self.env['product.product'].search([ ('categ_id.id', '=', category.id), ('active', '=', True) ])
                for product in products:
                    total_qty = total_amount = 0
                    worksheet.write(row, col, product.barcode, format_table_cell)
                    worksheet.write(row, col+1, product.name, format_table_cell)
                    worksheet.write(row, col+2, product.brand_id.name, format_table_cell)
                    worksheet.write(row, col+3, product.uom_id.name, format_table_cell)
                    index = 0
                    for location in locations:
                        qty = amount = 0
                        move = self.env['stock.move'].search([
                            ('product_id.id', '=', product.id),
                            ('location_id.id', '=', location.id),
                            ('location_dest_id.id', 'in', customer_loc_arr),
                            ('date', '>=', start_date_str),
                            ('date', '<=', end_date_str),
                        ])
                        for line in move: 
                            qty += line.product_uom_qty
                            for quant in line.quant_ids:
                                amount += quant.inventory_value

                        worksheet.write(row, col+4+index, qty, format_table_cell)
                        worksheet.write(row, col+5+index, amount, format_table_cell)
                    
                        total_qty += qty
                        total_amount += amount
                        total_amount_loc[location.id] += amount

                        index += 2
                    worksheet.write(row, col+4+index, total_qty, format_table_cell)
                    worksheet.write(row, col+5+index, total_amount, format_table_cell)
                    row += 1

        worksheet.merge_range(row, col, row+1, col+3, 'Total Amount/Location (Rp)', format_table_header)
        index = 0
        for location in locations:
            loc_name = location.location_id.name + '/' + location.name
            
            worksheet.merge_range(row, col+4+index, row, col+5+index, loc_name, format_table_header)
            worksheet.merge_range(row+1, col+4+index, row+1, col+5+index, total_amount_loc[location.id], format_table_header)
            index += 2

ReportSaleLocationXlsx('report.report_sale_location_xlsx', 'sale.location.wizard')
