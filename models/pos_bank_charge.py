from odoo import api, fields, models, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class PosBankCharge(models.Model):
    _name = "pos.bank.charge"
    _description = "Bank Charge on POS"
    _order = "name"

    name = fields.Char('Name', required=True)
    active = fields.Boolean('Active', default=1)
    journal_id = fields.Many2one('account.journal', string='Bank', domain=[('type', '=', 'bank')], required=True)
    line_ids = fields.One2many('pos.bank.charge.line', 'bank_charge_id', string='Configuration')
    config_ids = fields.Many2many('pos.config',
                                'pos_config_bank_charge_rel',
                                'bank_charge_id',
                                'config_id',
                                 string='POS Config')

class PosBankChargeLine(models.Model):
    _name = "pos.bank.charge.line"

    card_type = fields.Selection([
        ('same_credit', 'Credit on Us'),
        ('same_debit', 'Debit on Us'),
        ('other_credit', 'Credit off Us'),
        ('other_debit', 'Debit off Us'),
        ('qr', 'QRis'),
    ], string='Card Type', required=True)
    charge_type = fields.Selection([
        ('percent', 'Percentage'),
        ('fix', 'Fixed'),
    ], string='Charge Type', default='percent', required=True)
    value = fields.Float('Value', required=True)
    bank_charge_id = fields.Many2one('pos.bank.charge', string='Bank Charge', required=True, ondelete='cascade')
