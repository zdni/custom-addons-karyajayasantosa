from odoo import models, fields, api, tools, _

import logging
_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def action_server_member_card(self):
        if not self.card_number_lyt:
            self.member_status = True
            self.card_number_lyt = self.env['ir.sequence'].next_by_code('member.card.number')
            
