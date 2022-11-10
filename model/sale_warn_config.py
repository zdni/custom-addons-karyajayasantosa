from odoo import fields, models

class SaleWarnConfiguration(models.Model):
    _name = 'sale.warn.config'

    user_id = fields.Many2one('res.users', string='Partner')