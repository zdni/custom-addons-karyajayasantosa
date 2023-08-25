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

class ReportInventoryAdjustmentXlsx(ReportXlsx):

    def generate_xlsx_report(self, workbook, data, objects):
        form = data['form']

        # if len(form['location_ids']) == 0:
        #     locations = self.env['stock.location'].search([ ('usage', '=', 'internal') ])
        # else:
        #     locations = self.env['stock.location'].search([ ('id', 'in', form['location_ids']) ])
        
        # if len(form['product_ids']) == 0 and form['type'] == 'product':
        #     products = self.env['product.product'].search([ ('type', '=', 'product') ])
        # else:
        #     products = self.env['product.product'].search([ ('id', 'in', form['product_ids']) ])

        # if len(form['category_ids']) == 0 and form['type'] == 'category': 
        #     categories = self.env['product.category'].search([])
        # else:
        #     categories = self.env['product.category'].search([ ('id', 'in', form['category_ids']) ])

        condition_loc = [ ('usage', '=', 'internal') ] if len(form['location_ids']) == 0 else [ ('id', 'in', form['location_ids']) ]
        locations = self.env['stock.location'].search(condition_loc)
        
        end_date = datetime.strptime(form['end_date'], '%Y-%m-%d')
        end_date_str = ( end_date + timedelta( days=1, seconds=-1 ) ).strftime("%Y-%m-%d")

        row = col = 0
        format_title = workbook.add_format({'font_size': 22, 'bold': 1, 'align': 'center', 'valign': 'vcenter'})
        format_table_header = workbook.add_format({'font_size': 12, 'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vcenter'})
        format_table_cell = workbook.add_format({'font_size': 11, 'border': 1, 'valign': 'vcenter'})
        format_cell_bold = workbook.add_format({'font_size': 12, 'bold': 1, 'valign': 'vcenter'})
        format_cell_bold_center = workbook.add_format({'font_size': 12, 'bold': 1, 'valign': 'vcenter', 'align': 'center'})

        # title
        worksheet = workbook.add_worksheet("Inventory Detail")
        row += 2
        worksheet.merge_range(row, col, row+1, col+1+len(locations), 'Inventory Detail', format_title)
        row += 2
        worksheet.merge_range(row, col, row, col+1+len(locations), 'Tanggal Penarikan ' + str(form['end_date']), format_cell_bold_center)
        row += 3
        
        worksheet.write(row, col, "Produk", format_table_header)
        worksheet.write(row, col+1, "UoM", format_table_header)
        index = 0
        for location in locations:
            if location.name != 'Stock': continue
            loc_name = location.location_id.name + '/' + location.name
            worksheet.write(row, col+2+index, loc_name, format_table_header)
            index += 1

        row += 1
        if form['type'] == 'product':
            condition_prod = [ ('type', '=', 'product') ] if len(form['product_ids']) == 0 else [ ('id', 'in', form['product_ids']) ]
            products = self.env['product.product'].search(condition_prod)
            for product in products:
                worksheet.write(row, col, product.display_name, format_table_cell)
                worksheet.write(row, col+1, product.uom_id.name, format_table_cell)
                index = 0
                for location in locations:
                    if location.name != 'Stock': continue
                    
                    qty = 0
                    sq = self.env['stock.quant'].search([
                        ('product_id.id', '=', product.id),
                        ('location_id.id', '=', location.id),
                        ('in_date', '<=', end_date_str),
                    ])
                    for line in sq: qty += line.qty

                    worksheet.write(row, col+2+index, qty, format_table_cell)
                    index += 1
                row += 1
        
        if form['type'] == 'category':
            condition_cat = [] if len(form['category_ids']) == 0 else [ ('id', 'in', form['category_ids']) ]
            categories = self.env['product.category'].search(condition_cat)
            for category in categories:
                products = self.env['product.product'].search([ ('categ_id.id', '=', category.id) ])
                for product in products:
                    worksheet.write(row, col, product.display_name, format_table_cell)
                    worksheet.write(row, col+1, product.uom_id.name, format_table_cell)
                    index = 0
                    for location in locations:
                        if location.name != 'Stock': continue

                        qty = 0
                        sq = self.env['stock.quant'].search([
                            ('product_id.id', '=', product.id),
                            ('location_id.id', '=', location.id),
                            ('in_date', '<=', end_date_str),
                        ])
                        for line in sq: qty += line.qty

                        worksheet.write(row, col+2+index, qty, format_table_cell)
                        index += 1
                    row += 1
        
ReportInventoryAdjustmentXlsx('report.report_inventory_detail_xlsx', 'inventory.detail.wizard')
