from odoo import api, fields, models, _

import logging
_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    total_deposit = fields.Float('Deposit', compute='_calculate_total_deposit')
    
    @api.multi
    def _calculate_total_deposit(self):
        for partner in self:
            lines = self.env['account.deposit.line'].search([
                ('partner_id.id', '=', partner.id)
            ], order='date asc')
            total_deposit = 0
            
            for line in lines:
                total_deposit += (line.debit - line.credit)

            partner.total_deposit = total_deposit