from odoo import api, fields, models, _
import time
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    recipient = fields.Char('Recipient')
    phone_number = fields.Char('Phone Number')
    delivery_address = fields.Char('Delivery Address')
    delivery_date = fields.Datetime('Delivery Date')
    picking_data = fields.Text("Picking Data", readonly=True)

    @api.multi
    def action_refresh_picking_data(self):
        tmpl = self.env['mail.template'].search([('name','=','Dot Matrix Picking Note')])
        data = tmpl.render_template( tmpl.body_html, 'stock.picking', self.id )
        self.picking_data = data

    @api.multi
    def dummy_picking(self):
        pass

    @api.multi
    def button_confirm(self):
        res = super(StockPicking, self).button_confirm()
        self.action_refresh_picking_data()
        return res
