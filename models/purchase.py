from datetime import datetime, timedelta

from odoo import fields, models, api

import logging
_logger = logging.getLogger(__name__)

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.onchange('product_id', 'product_uom')
    def _onchange_quantity(self):
        super(PurchaseOrderLine, self)._onchange_quantity()
        if not self.product_id:
            return
        
        price_unit = self.product_id.product_tmpl_id.standard_price_pricelist
        self.price_unit = price_unit
        
        # now = datetime.now() + timedelta(hours=8)
        # current_time = now.strftime("%Y-%m-%d %H:%M:%S")
        # query = """
        #     SELECT schedule_pricelist_product.start_date,
        #         schedule_pricelist_product.end_date,
        #         schedule_pricelist_product_line.product_id,
        #         schedule_pricelist_product_line.purchase_price,
        #         schedule_pricelist_product_line.selling_price
        #     FROM schedule_pricelist_product_line
        #     JOIN schedule_pricelist_product ON schedule_pricelist_product.id = schedule_pricelist_product_line.pricelist_id
        #     WHERE schedule_pricelist_product_line.product_id = %s
        #         AND schedule_pricelist_product.start_date >= %s
        #     ORDER BY schedule_pricelist_product.start_date DESC
        #     LIMIT 1
        # """
        # params = [ self.product_id.id, current_time ]
        # self.env.cr.execute( query, params )
        # line = self.env.cr.dictfetchall()
        
        # if line:
        #     self.price_unit = line[0]['purchase_price']
        # else:
        #     line = self.env['schedule.pricelist.product.line'].search([
        #         ('product_id', '=', self.product_id.id)
        #     ], limit=1, order='id desc')
        #     if line:
        #         self.price_unit = line.purchase_price