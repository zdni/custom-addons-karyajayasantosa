from odoo import api, models

class MarketingAgentReportTemp(models.TransientModel):
    _name = "report.marketing_agent.marketing_agent_report_temp"
    
    @api.model
    def render_html(self, docids, data=None):
        docargs = {
            'doc_ids': data.get('ids'),
            'doc_model': data.get('model'),
            'data': data['form'],
            'start_date': data['start_date'],
            'end_date': data['end_date'],
        }
        return self.env['report'].render('marketing_agent.marketing_agent_report_temp', docargs)