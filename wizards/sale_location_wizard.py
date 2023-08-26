from odoo import api, fields, models, _
from datetime import datetime, timedelta

import logging
_logger = logging.getLogger(__name__)

class SaleLocationWizard(models.TransientModel):
    _name = "sale.location.wizard"

    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date('End Date', required=True)
    location_ids = fields.Many2many('stock.location', string='Location')
    product_ids = fields.Many2many('product.product', string='Product')
    category_ids = fields.Many2many('product.category', string='Category')
    type = fields.Selection([
        ('product', 'Product'),
        ('category', 'Category'),
    ], string='Option', default='product', required=True)

    
    @api.multi
    def print_report_xlsx(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'sale.location.wizard'
        datas['form'] = self.read()[0]
        
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'report_sale_location_xlsx',
            'datas': datas,
        }