from odoo.exceptions import UserError
from odoo import api, fields, models, _

import logging
_logger = logging.getLogger(__name__)

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    discount_view = fields.Selection([('after', 'After Tax')], string='Discount Type')
    discount_type = fields.Selection([('fixed', 'Fixed'), ('percentage', 'Percentage')], string='Discount Method')                                     
    discount_value = fields.Float(string='Discount Value', store=True)
    discounted_amount = fields.Float(compute='disc_amount', string='Discounted Amount', store=True, readonly=True)

    @api.depends('order_line.price_subtotal', 'discount_type', 'discount_value')
    def _amount_all(self):
        for purchase in self:
            
            amount_untaxed = amount_tax  = amount_total = 0.0
            for line in purchase.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax

            if purchase.discount_view == 'after':
                if purchase.discount_type == 'fixed':
                    amount_total = amount_untaxed + amount_tax - purchase.discount_value
                elif purchase.discount_type == 'percentage':
                    if purchase.discount_value < 100:
                        amount_to_dis = (amount_untaxed + amount_tax) * (purchase.discount_value / 100)
                        amount_total = (amount_untaxed+ amount_tax) - amount_to_dis
                    else:
                        raise UserError(_('Discount percentage should not be greater than 100.'))
                else:
                    amount_total = amount_untaxed + amount_tax
            else:
                amount_total = amount_untaxed + amount_tax
            purchase.update({
                'amount_untaxed': purchase.currency_id.round(amount_untaxed),
                'amount_tax': purchase.currency_id.round(amount_tax),
                'amount_total': amount_total,
            })

    @api.one
    @api.depends('order_line.price_subtotal', 'discount_type', 'discount_value')
    def disc_amount(self):
        val = 0
        for line in self.order_line:
            val += line.price_tax
        if self.discount_view == 'after':
            if self.discount_type == 'fixed':
                self.discounted_amount = self.discount_value
            elif self.discount_type == 'percentage':
                amount_to_dis = (self.amount_untaxed + val) * (self.discount_value / 100)
                self.discounted_amount = amount_to_dis
            else:
                self.discounted_amount = 0
        else:
            self.discounted_amount = 0