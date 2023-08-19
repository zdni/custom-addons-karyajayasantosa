from odoo import api, fields, models, _
from datetime import datetime, timedelta

import logging
_logger = logging.getLogger(__name__)

class InventoryDetailWizard(models.TransientModel):
    _name = "inventory.detail.wizard"

    end_date = fields.Date('End Date', required=True)
    location_ids = fields.Many2many('stock.location', string='Location')
    product_ids = fields.Many2many('product.product', string='Product')
    category_ids = fields.Many2many('product.category', string='Category')
    type = fields.Selection([
        ('product', 'Product'),
        ('category', 'Category'),
    ], string='Option', default='product', required=True)

    @api.multi
    def print_report(self):
        end_date = datetime.strptime(self.end_date, '%Y-%m-%d')
        end_date_str = ( end_date + timedelta( days=1, seconds=-1 ) ).strftime("%Y-%m-%d")
        end_date_obj = ( end_date + timedelta( days=1, seconds=-1 ) )
        groupby_dict = {}
        
        if len(self.location_ids) == 0:
            self.location_ids = self.env['stock.location'].search([ ('usage', '=', 'internal') ])
        
        if len(self.product_ids) == 0 and self.type == 'product':
            self.product_ids = self.env['product.product'].search([ ('type', '=', 'product') ])

        if len(self.category_ids) == 0 and self.type == 'category':
            self.category_ids = self.env['product.category'].search([])

        for location in self.location_ids:
            loc_name = location.location_id.name + '/' + location.name
            if not (loc_name in groupby_dict):
                groupby_dict[loc_name] = []

            qty = 0
            amount = 0
            if self.type == 'product':
                for product in self.product_ids:
                    sq = self.env['stock.quant'].search([
                        ('product_id.id', '=', product.id),
                        ('location_id.id', '=', location.id),
                        ('in_date', '<=', end_date_str),
                    ])
                    for line in sq:
                        qty += line.qty
                        amount += line.inventory_value

                    data = {
                        'product': product.name,
                        'uom': product.uom_id.name,
                        'qty': qty,
                        'amount': amount,
                    }
                    groupby_dict[loc_name].append(data)

            if self.type == 'category':
                for category in self.category_ids:
                    products = self.env['product.product'].search([ ('categ_id.id', '=', category.id) ])
                    for product in products:
                        sq = self.env['stock.quant'].search([
                            ('product_id.id', '=', product.id),
                            ('location_id.id', '=', location.id),
                            ('in_date', '<=', end_date_str),
                        ])
                        for line in sq:
                            qty += line.qty
                            amount += line.inventory_value

                        data = {
                            'product': product.name,
                            'uom': product.uom_id.name,
                            'qty': 0,
                            'amount': 0,
                        }
                        groupby_dict[loc_name].append(data)

        datas = {
            'ids': self.ids,
            'model': 'inventory.detail.wizard',
            'form': groupby_dict,
            'date': str( self.end_date ),
        }
        return self.env['report'].get_action(self, 'report_inventory.report_inventory_detail', data=datas)