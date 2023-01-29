from odoo import api, fields, models

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_marketing_agent = fields.Boolean('Marketing Agent')