from odoo import fields, models

class PosConfig(models.Model):
    _inherit = "pos.config"

    enable_pos_bank_charge = fields.Boolean("Enable Bank Charge")
    bank_charge_product_id = fields.Many2one("product.product","Bank Charge Product")

    bank_charge_ids = fields.Many2many('pos.bank.charge', 
                                'pos_config_bank_charge_rel',
                                'config_id',
                                'bank_charge_id',
                                string='POS Bank Charge')