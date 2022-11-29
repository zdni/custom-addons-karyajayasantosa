from odoo import models, fields, api, tools, _

import logging
_logger = logging.getLogger(__name__)

class POSSession(models.Model):
    _inherit = 'pos.session'

    # @api.multi
    # def custom_close_pos_session(self):
    #     self._check_pos_session_balance()
    #     for session in self:
    #         session.write({'state': 'closing_control', 'stop_at': fields.Datetime.now()})
    #         if not session.config_id.cash_control:
    #             session.action_pos_session_close()
    #             return True
    #         if session.config_id.cash_control:
    #             self._check_pos_session_balance()
    #             return self.action_pos_session_close()

    # @api.multi
    # def cash_control_line(self, vals):
    #     total_amount = 0.00
    #     if vals:
    #         self.cashcontrol_ids.unlink()
    #         for data in vals:
    #             self.env['custom.cashcontrol'].create(data)
    #     for cash_line in self.cashcontrol_ids:
    #         total_amount += cash_line.subtotal
    #     for statement in self.statement_ids:
    #         statement.write({'balance_end_real': total_amount})
    #     return True

    @api.multi
    def print_z_report(self):
        _logger.warning('print_z_report')