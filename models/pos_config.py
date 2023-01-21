from odoo import fields, models, api

import logging
_logger = logging.getLogger(__name__)

class PosConfig(models.Model):
    _inherit = "pos.config"

    disc_product_id = fields.Many2one('product.product', string='Discount Product', required=True)
    
    enable_pos_discount_global = fields.Boolean("Enable Global Discount")
    min_order_disc_global = fields.Float('Minimum Order Disc Global')

    promotion_manual_select = fields.Boolean('Select Manual Promotion', default=True)
    promotion_ids = fields.Many2many('pos.promotion',
                                     'pos_config_promotion_rel',
                                     'config_id',
                                     'promotion_id',
                                     string='POS Promotion')

    enable_pos_voucher = fields.Boolean('Enable POS Voucher')
    voucher_journal_id = fields.Many2one("account.journal","Voucher Journal")

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    @api.model
    def name_search(self, name,args=None, operator='ilike', limit=100):
        if self._context.get('voucher_jr'):
            if self._context.get('journal_ids') and \
               self._context.get('journal_ids')[0] and \
               self._context.get('journal_ids')[0][2]:
               args += [['id', 'in', self._context.get('journal_ids')[0][2]]]
            else:
                return False
        return super(AccountJournal, self).name_search(name, args=args, operator=operator, limit=limit)
