from odoo import api, fields, models, _
from datetime import date, timedelta
import logging

_logger = logging.getLogger(__name__)

class MarketingAgentReport(models.TransientModel):
    _name = 'marketing.agent.report'

    marketing_agent_ids = fields.Many2many('res.partner', string='Marketing Agent', domain="[('is_marketing_agent', '=', True)]")
    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date('End Date', required=True)

    @api.multi
    def print_marketing_agent_report(self):
        result = {}
        salesperson = ''

        if len( self.marketing_agent_ids ) < 1:
            self.marketing_agent_ids = self.env['res.partner'].search([
                ('is_marketing_agent', '=', True)
            ])

        for agent in self.marketing_agent_ids:
            _logger.warning( agent )
            salesperson = agent.name

            orders = self.env['pos.order'].search([
                ('agent_id', '=', agent.id),
                ('date_order', '>=', self.start_date),
                ('date_order', '<=', self.end_date),
            ])
            for order in orders:
                data = [
                    order.name,
                    order.date_order,
                    order.amount_total,
                ]

                if data and salesperson:
                    if salesperson in result:
                        result[salesperson].append(data)
                    else:
                        result[salesperson] = [data]
        
        _logger.warning( result )
        
        datas = {
            'ids': self.ids,
            'model': 'marketing.agent.report',
            'form': result,
            'start_date': self.start_date,
            'end_date': self.end_date,
        }
        return self.env['report'].get_action(self, 'marketing_agent.marketing_agent_report_temp', data=datas)