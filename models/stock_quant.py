from odoo import api, fields, models

import logging
_logger = logging.getLogger(__name__)

class Quant(models.Model):
    _inherit = "stock.quant"

    cost = fields.Float(string="Total Cost") #, compute="count_cost"
    ship_cost = fields.Float(string="Shipping Cost", compute="count_cost") #
    total_cost = fields.Float(string="Cost per Product", compute="count_cost") #

    @api.one
    def count_cost(self):
        res = super(Quant, self).count_cost()

        total_ship_cost = 0

        if len(self.history_ids) > 1:
            for hist_id in self.history_ids:
                picking_name = hist_id.picking_id.name
                custom_landed_costs = self.env['custom.landed.cost'].search([('picking_ids.name', '=', picking_name)])
                
                if custom_landed_costs:
                    for landed_cost in custom_landed_costs:
                        for line in landed_cost.valuation_adjustment_lines:
                            if line.product_id.name == self.product_id.name:
                                total_ship_cost += line.additional_landed_cost/line.quantity
                else:
                    landed_costs = self.env['stock.landed.cost'].search([('picking_ids.name', '=', picking_name)])
                    for landed_cost in landed_costs:
                        for line in landed_cost.valuation_adjustment_lines:
                            if line.product_id.name == self.product_id.name:
                                total_ship_cost += line.additional_landed_cost/line.quantity

        else:
            picking_name = self.history_ids.picking_id.name
            custom_landed_costs = self.env['custom.landed.cost'].search([('picking_ids.name', '=', picking_name)])

            if custom_landed_costs:
                for line in custom_landed_costs.valuation_adjustment_lines:
                    if line.product_id.name == self.product_id.name:
                        total_ship_cost += line.additional_landed_cost/line.quantity
            else:
                landed_costs = self.env['stock.landed.cost'].search([('picking_ids.name', '=', picking_name)])
                for line in landed_costs.valuation_adjustment_lines:
                    if line.product_id.name == self.product_id.name:
                        total_ship_cost += line.additional_landed_cost/line.quantity
            
        if total_ship_cost > 0:
            self.ship_cost = total_ship_cost
        self.total_cost = (self.inventory_value/self.qty)-total_ship_cost
    
        return res