from odoo import api, fields, models

class AccountPayment(models.Model):
    _inherit = "account.payment"

    settled = fields.Boolean(
        string="Settled", readonly=True, default=False)
