from odoo import api, fields, models

import logging
_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    canvas_price = fields.Float(string="Canvas Price", compute="get_canvas_price")

    @api.one
    def get_canvas_price(self):
        canvas_pricelist = self.env['product.pricelist'].search([('name', '=', 'Harga Kampas')])
        product_pricelist_item = self.env['product.pricelist.item'].search([
            ('pricelist_id', '=', canvas_pricelist.id),
            ('product_tmpl_id.name', '=', self.name)
        ], limit=1)
        self.canvas_price = product_pricelist_item.fixed_price

        # for line in canvas_pricelist.item_ids:
        #     product = self.env['product.template'].search([('name', '=', line.name)])
        #     product.canvas_price = line.fixed_price
            