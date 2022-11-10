from odoo import fields, models, api
from datetime import datetime, timedelta

import logging
_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    config_member = fields.Selection(
        [ 
            ('loyalty', 'Member Loyalty'), 
            ('cashback', 'Member Cashback')
        ], 'Member', default='loyalty')
    member_status = fields.Boolean(string='Member Status', default=False)