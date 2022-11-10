 # -*- coding: utf-8 -*-
from collections import namedtuple
from datetime import datetime
from dateutil import relativedelta

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

import logging

_logger = logging.getLogger(__name__)

class InternalTransfer(models.Model):
    _name = "stock.internal.reorder.transfer"

    @api.model
    def run_scheduler(self, use_new_cursor=False, company_id=False):
        return {}