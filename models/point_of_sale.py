from odoo import fields, models, api
from datetime import datetime, timedelta
import logging
_logger = logging.getLogger(__name__)

class PosConfig(models.Model):
    _inherit = "pos.config"

    enable_pos_picking_note = fields.Boolean("Enable POS Picking Note")
    picking_note_msg = fields.Char('Message in Orderline note')