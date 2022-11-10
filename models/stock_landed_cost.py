from collections import defaultdict

from odoo import api, fields, models, tools, _
from odoo.addons import decimal_precision as dp
from odoo.addons.custom_landed_costs.models import product
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class LandedCost(models.Model):
    _name = 'custom.landed.cost'
    _description = 'Stock Landed Cost'
    _inherit = 'mail.thread'

    name = fields.Char(
        'Name', default=lambda self: _('New'),
        copy=False, readonly=True, track_visibility='always')
    date = fields.Date(
        'Date', default=fields.Date.context_today,
        copy=False, required=True, states={'done': [('readonly', True)]}, track_visibility='onchange')
    picking_ids = fields.Many2many(
        'stock.picking', string='Pickings',
        copy=False, states={'done': [('readonly', True)]})
    purchase_order_ids = fields.Many2many('purchase.order', string='Purchase Order', copy=False, readonly=True)
    cost_lines = fields.One2many(
        'custom.landed.cost.lines', 'cost_id', 'Cost Lines',
        copy=True, states={'done': [('readonly', True)]})
    valuation_adjustment_lines = fields.One2many(
        'custom.valuation.adjustment.lines', 'cost_id', 'Valuation Adjustments',
        states={'done': [('readonly', True)]})
    description = fields.Text(
        'Item Description', states={'done': [('readonly', True)]})
    amount_total = fields.Float(
        'Total', compute='_compute_total_amount',
        digits=0, store=True, track_visibility='always')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Posted'),
        ('cancel', 'Cancelled')], 'State', default='draft',
        copy=False, readonly=True, track_visibility='onchange')
    account_invoice_id = fields.Many2one(
        'account.invoice', 'Journal Payment',
        copy=False, readonly=True)
    partner_id = fields.Many2one('res.partner', required=True, string='Ekspedisi')

    def get_purchase_order_ids(self):
        purchase_orders = []
        for picking_id in self.picking_ids:
            purchase_orders.append( picking_id.purchase_id.id )
        
        return purchase_orders

    @api.one
    @api.depends('cost_lines.price_unit')
    def _compute_total_amount(self):
        self.amount_total = sum(line.price_unit for line in self.cost_lines)

    @api.onchange('picking_ids')
    def _onchange_picking_ids(self):
        purchase_orders = self.get_purchase_order_ids()
        
        self.purchase_order_ids = [(6, 0, purchase_orders)]

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('custom.landed.cost')
        
        purchase_orders = []
        for picking_id in vals['picking_ids'][0][2]:
            picking = self.env['stock.picking'].search([
                ('id', '=', picking_id)
            ])
            purchase_orders.append( picking.purchase_id.id )
        vals['purchase_order_ids'] = [(6, 0, purchase_orders)]
        
        return super(LandedCost, self).create(vals)

    @api.multi
    def unlink(self):
        self.button_cancel()
        return super(LandedCost, self).unlink()

    @api.multi
    def _track_subtype(self, init_values):
        if 'state' in init_values and self.state == 'done':
            return 'custom_landed_costs.mt_custom_landed_cost_open'
        return super(LandedCost, self)._track_subtype(init_values)

    @api.multi
    def button_cancel(self):
        if any(cost.state == 'done' for cost in self):
            raise UserError(
                _('Validated landed costs cannot be cancelled, but you could create negative landed costs to reverse them'))
        return self.write({'state': 'cancel'})

    @api.multi
    def button_validate(self):
        if any(cost.state != 'draft' for cost in self):
            raise UserError(_('Only draft landed costs can be validated'))
        if any(not cost.valuation_adjustment_lines for cost in self):
            raise UserError(_('No valuation adjustments lines. You should maybe recompute the landed costs.'))
        if not self._check_sum():
            raise UserError(_('Cost and adjustments lines do not match. You should maybe recompute the landed costs.'))

        for cost in self:
            invoice_lines = []
            for line in cost.cost_lines:
                invoice_lines.append( (0, 0, {
                    'account_id': line.product_id.property_account_expense_id.id,
                    'product_id': line.product_id.id,
                    'name': cost.name + ': ' + line.product_id.name,
                    'quantity': 1,
                    'uom_id': line.product_id.uom_id.id,
                    'price_unit': line.price_unit,
                }) )

            bill = self.env['account.invoice']
            bill_vals = {
                'partner_id': cost.partner_id.id,
                'origin': cost.name,
                'journal_id': 3,
                'invoice_line_ids': invoice_lines,
                'amount_untaxed': cost.amount_total,
                'amount_tax': 0,
                'amount_total': cost.amount_total,
                'account_id': 251,
                'date': '',
                'date_invoice': '',
                'state': 'draft',
                'type': 'in_invoice',
            }
            bill = bill.create(bill_vals)

            for line in cost.valuation_adjustment_lines.filtered(lambda line: line.move_id):
                per_unit = line.final_cost / line.quantity
                diff = per_unit - line.former_cost_per_unit

                curr_rounding = line.move_id.company_id.currency_id.rounding
                diff_rounded = tools.float_round(diff, precision_rounding=curr_rounding)
                diff_correct = diff_rounded
                quants = line.move_id.quant_ids.sorted(key=lambda r: r.qty, reverse=True)
                quant_correct = False
                if quants\
                        and tools.float_compare(quants[0].product_id.uom_id.rounding, 1.0, precision_digits=1) == 0\
                        and tools.float_compare(line.quantity * diff, line.quantity * diff_rounded, precision_rounding=curr_rounding) != 0\
                        and tools.float_compare(quants[0].qty, 2.0, precision_rounding=quants[0].product_id.uom_id.rounding) >= 0:
                    # Search for existing quant of quantity = 1.0 to avoid creating a new one
                    quant_correct = quants.filtered(lambda r: tools.float_compare(r.qty, 1.0, precision_rounding=quants[0].product_id.uom_id.rounding) == 0)
                    if not quant_correct:
                        quant_correct = quants[0]._quant_split(quants[0].qty - 1.0)
                    else:
                        quant_correct = quant_correct[0]
                        quants = quants - quant_correct
                    diff_correct += (line.quantity * diff) - (line.quantity * diff_rounded)
                    diff = diff_rounded

                quant_dict = {}
                for quant in quants:
                    quant_dict[quant] = quant.cost + diff
                if quant_correct:
                    quant_dict[quant_correct] = quant_correct.cost + diff_correct
                for quant, value in quant_dict.items():
                    quant.sudo().write({'cost': value})
                qty_out = 0
                for quant in line.move_id.quant_ids:
                    if quant.location_id.usage != 'internal':
                        qty_out += quant.qty
                
            purchase_orders = self.get_purchase_order_ids()
            cost.write({'state': 'done', 'account_invoice_id': bill.id, 'purchase_order_ids': [(6, 0, purchase_orders)]})
            bill.action_invoice_open()
        return True

    def _check_sum(self):
        """ Check if each cost line its valuation lines sum to the correct amount
        and if the overall total amount is correct also """
        prec_digits = self.env['decimal.precision'].precision_get('Account')
        for landed_cost in self:
            total_amount = sum(landed_cost.valuation_adjustment_lines.mapped('additional_landed_cost'))
            if not tools.float_compare(total_amount, landed_cost.amount_total, precision_digits=prec_digits) == 0:
                return False

            val_to_cost_lines = defaultdict(lambda: 0.0)
            for val_line in landed_cost.valuation_adjustment_lines:
                val_to_cost_lines[val_line.cost_line_id] += val_line.additional_landed_cost
            if any(tools.float_compare(cost_line.price_unit, val_amount, precision_digits=prec_digits) != 0
                   for cost_line, val_amount in val_to_cost_lines.iteritems()):
                return False
        return True

    def get_valuation_lines(self):
        lines = []

        for move in self.mapped('picking_ids').mapped('move_lines'):
            # it doesn't make sense to make a landed cost for a product that isn't set as being valuated in real time at real cost
            if move.product_id.valuation != 'real_time' or move.product_id.cost_method != 'real':
                continue
            vals = {
                'product_id': move.product_id.id,
                'move_id': move.id,
                'quantity': move.product_qty,
                'former_cost': sum(quant.cost * quant.qty for quant in move.quant_ids),
                'weight': move.product_id.weight * move.product_qty,
                'volume': move.product_id.volume * move.product_qty
            }
            lines.append(vals)

        if not lines and self.mapped('picking_ids'):
            raise UserError(_('The selected picking does not contain any move that would be impacted by landed costs. Landed costs are only possible for products configured in real time valuation with real price costing method. Please make sure it is the case, or you selected the correct picking'))
        return lines

    @api.multi
    def compute_landed_cost(self):
        AdjustementLines = self.env['custom.valuation.adjustment.lines']
        AdjustementLines.search([('cost_id', 'in', self.ids)]).unlink()

        digits = dp.get_precision('Product Price')(self._cr)
        towrite_dict = {}
        divide_dict = {}
        for cost in self.filtered(lambda cost: cost.picking_ids):
            total_qty = 0.0
            total_cost = 0.0
            total_weight = 0.0
            total_volume = 0.0
            total_line = 0.0
            all_val_line_values = cost.get_valuation_lines()
            for val_line_values in all_val_line_values:
                for cost_line in cost.cost_lines:
                    val_line_values.update({'cost_id': cost.id, 'cost_line_id': cost_line.id})
                    self.env['custom.valuation.adjustment.lines'].create(val_line_values)
                total_qty += val_line_values.get('quantity', 0.0)
                total_weight += val_line_values.get('weight', 0.0)
                total_volume += val_line_values.get('volume', 0.0)

                former_cost = val_line_values.get('former_cost', 0.0)
                # round this because former_cost on the valuation lines is also rounded
                total_cost += tools.float_round(former_cost, precision_digits=digits[1]) if digits else former_cost

                total_line += 1

            for line in cost.cost_lines:
                value_split = 0.0
                for valuation in cost.valuation_adjustment_lines:
                    value = 0.0
                    if valuation.cost_line_id and valuation.cost_line_id.id == line.id:
                        if line.split_method == 'by_quantity' and total_qty:
                            per_unit = (line.price_unit / total_qty)
                            value = valuation.quantity * per_unit
                        elif line.split_method == 'by_weight' and total_weight:
                            per_unit = (line.price_unit / total_weight)
                            value = valuation.weight * per_unit
                        elif line.split_method == 'by_volume' and total_volume:
                            per_unit = (line.price_unit / total_volume)
                            value = valuation.volume * per_unit
                        elif line.split_method == 'equal':
                            value = (line.price_unit / total_line)
                        elif line.split_method == 'by_current_cost_price' and total_cost:
                            per_unit = (line.price_unit / total_cost)
                            value = valuation.former_cost * per_unit
                        else:
                            value = (line.price_unit / total_line)

                        if digits:
                            value = tools.float_round(value, precision_digits=digits[1], rounding_method='UP')
                            fnc = min if line.price_unit > 0 else max
                            value = fnc(value, line.price_unit - value_split)
                            value_split += value

                        if valuation.id not in towrite_dict:
                            towrite_dict[valuation.id] = value
                            divide_dict[valuation.id] = valuation.quantity or valuation.weight or valuation.volume or valuation.former_cost
                        else:
                            towrite_dict[valuation.id] += value
        if towrite_dict:
            for key, value in towrite_dict.items():
                AdjustementLines.browse(key).write({'additional_landed_cost': value})
                
                divide = divide_dict[key] or 1.0
                AdjustementLines.browse(key).write({'additional_landed_cost_per_unit': value/divide})

        return True


class LandedCostLine(models.Model):
    _name = 'custom.landed.cost.lines'
    _description = 'Stock Landed Cost Lines'

    name = fields.Char('Description')
    cost_id = fields.Many2one(
        'custom.landed.cost', 'Landed Cost',
        required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', 'Product', required=True)
    price_unit = fields.Float('Cost', digits=dp.get_precision('Product Price'), required=True)
    split_method = fields.Selection(product.SPLIT_METHOD, string='Split Method', required=True)
    account_id = fields.Many2one('account.account', 'Account', domain=[('deprecated', '=', False)])

    @api.onchange('product_id')
    def onchange_product_id(self):
        if not self.product_id:
            self.quantity = 0.0
        self.name = self.product_id.name or ''
        self.split_method = self.product_id.split_method or 'equal'
        self.price_unit = self.product_id.standard_price or 0.0
        self.account_id = self.product_id.property_account_expense_id.id or self.product_id.categ_id.property_account_expense_categ_id.id


class AdjustmentLines(models.Model):
    _name = 'custom.valuation.adjustment.lines'
    _description = 'Stock Valuation Adjustment Lines'

    name = fields.Char(
        'Description', compute='_compute_name', store=True)
    cost_id = fields.Many2one(
        'custom.landed.cost', 'Landed Cost',
        ondelete='cascade', required=True)
    cost_line_id = fields.Many2one(
        'custom.landed.cost.lines', 'Cost Line', readonly=True)
    move_id = fields.Many2one('stock.move', 'Stock Move', readonly=True)
    product_id = fields.Many2one('product.product', 'Product', required=True)
    quantity = fields.Float(
        'Quantity', default=1.0,
        digits=0, required=True)
    weight = fields.Float(
        'Weight', default=1.0,
        digits=dp.get_precision('Stock Weight'))
    volume = fields.Float(
        'Volume', default=1.0)
    former_cost = fields.Float(
        'Former Cost', digits=dp.get_precision('Product Price'))
    former_cost_per_unit = fields.Float(
        'Former Cost(Per Unit)', compute='_compute_former_cost_per_unit',
        digits=0, store=True)
    additional_landed_cost = fields.Float(
        'Add. Landed Cost',
        digits=dp.get_precision('Product Price'))
    additional_landed_cost_per_unit = fields.Float(
        'Add. Landed Cost (Per Unit)',
        digits=dp.get_precision('Product Price'))
    final_cost = fields.Float(
        'Final Cost', compute='_compute_final_cost',
        digits=0, store=True)

    @api.one
    @api.depends('cost_line_id.name', 'product_id.code', 'product_id.name')
    def _compute_name(self):
        name = '%s - ' % (self.cost_line_id.name if self.cost_line_id else '')
        self.name = name + (self.product_id.code or self.product_id.name or '')

    @api.one
    @api.depends('former_cost', 'quantity')
    def _compute_former_cost_per_unit(self):
        self.former_cost_per_unit = self.former_cost / (self.quantity or 1.0)

    @api.one
    @api.depends('former_cost', 'additional_landed_cost')
    def _compute_final_cost(self):
        self.final_cost = self.former_cost + self.additional_landed_cost