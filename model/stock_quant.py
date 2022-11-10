from odoo import api, fields, models

import logging
_logger = logging.getLogger(__name__)

class Quant(models.Model):
    _inherit = "stock.quant"

    cost = fields.Float(string="Total Cost") #, compute="count_cost"
    _ship_cost = fields.Float(string="Shipping Cost", compute="count_cost") #
    _total_cost = fields.Float(string="Cost per Product", compute="count_cost") #
    # ship_cost = fields.Float(string="Shipping Cost", related='_ship_cost') #
    # total_cost = fields.Float(string="Cost per Product", related='_total_cost') #, related='compute_total_cost'


    @api.multi
    def count_cost(self):
        for record in self:
            total_ship_cost = 0
            for hist_id in record.history_ids:
                picking_name = hist_id.picking_id.name
                qty = hist_id.product_uom_qty
                
                line = self.env['stock.valuation.adjustment.lines'].search([
                    ('product_id.id', '=', record.product_id.id),
                    ('quantity', '=', qty),
                    ('cost_id.picking_ids.name', '=', picking_name)
                ], limit=1)
                if line:
                    total_ship_cost += (line.additional_landed_cost/line.quantity)
                    # total_ship_cost += line.additional_landed_cost_per_unit
                
                else:
                    line = self.env['custom.valuation.adjustment.lines'].search([
                        ('product_id.id', '=', record.product_id.id),
                        ('quantity', '=', qty),
                        ('cost_id.picking_ids.name', '=', picking_name)
                    ], limit=1)
                    total_ship_cost += line.additional_landed_cost_per_unit

            total_cost = (record.inventory_value/record.qty)-total_ship_cost

            record._ship_cost = total_ship_cost
            record._total_cost = total_cost