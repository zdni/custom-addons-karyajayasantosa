from odoo import fields, models, api

import logging
_logger = logging.getLogger(__name__)

class PosOrder(models.Model):
    _inherit = "pos.order"

    total_savings = fields.Float('Total Savings')