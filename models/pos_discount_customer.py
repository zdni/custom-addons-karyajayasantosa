from odoo import api, fields, models, _, exceptions

import logging
_logger = logging.getLogger(__name__)

class PosDiscountCustomer(models.Model):
    _name = "pos.discount_customer"

    name = fields.Char(string='POS Discount Customer Reference', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    discount_type = fields.Selection([
        ('fix', 'Fixed'),
        ('percent', 'Percentage'),
    ], string='Discount Type', default="fix", required=True)
    discount_value = fields.Float('Discount Value', required=True)
    partner_ids = fields.Many2many('res.partner', string='Customer')
    status = fields.Boolean('Status', default=True)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('pos.discount_customer') or _('New')

        result = super(PosDiscountCustomer, self).create(vals)
        return result
    
    @api.onchange('discount_value')
    def _onchange_discount_value(self):
        if self.discount_type == 'percent' and (self.discount_value > 100 or self.discount_value < 0):
            raise exceptions.UserError('Discount Value not validated')