from odoo import api, fields, models, _
from datetime import datetime, timedelta

import logging
_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    recipient = fields.Char('Recipient')
    phone_number = fields.Char('Phone Number')
    delivery_address = fields.Char('Delivery Address')
    delivery_date = fields.Datetime('Delivery Date')
    delivery_date_str = fields.Char('Delivery DAte Str')
    picking_data = fields.Text("Picking Data", readonly=True)

    @api.multi
    def write(self, values):
        if 'delivery_date' in values and values['delivery_date']:
            date_time_str = values['delivery_date']
            date_time = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
            original_date_time = date_time + timedelta(hours=8)
            original_date_time_str = original_date_time.strftime('%Y-%m-%d %H:%M:%S')
            values['delivery_date_str'] = original_date_time_str
        
        return super(StockPicking, self).write(values)

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
