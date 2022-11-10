from odoo import api, exceptions, fields, models, _

class CommissionSettlement(models.Model):
    _name = 'sale.commission.settlement'

    name = fields.Char('Name')