from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)
class DueDateCustomer(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    @api.one
    def _get_invisible_sale_warn(self):
        block_user = self.env['sale.warn.config'].search([
            ('user_id.id', '=', self.env.user.id)
        ])
        if block_user:
            self.invisible_sale_warn = False
        else:
            self.invisible_sale_warn = True

    due_date_customer = fields.Integer('due date', default=60)
    invisible_sale_warn = fields.Boolean('Invisible Sale Warn', compute='_get_invisible_sale_warn')

