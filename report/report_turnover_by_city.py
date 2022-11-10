from odoo import api, models


class ReportSalesSalespersonWise(models.AbstractModel):
    _name = 'report.report_turnover_by_city.temp_report_turnover_by_city'

    @api.model
    def render_html(self, docids, data=None):
        docargs =  {
            'doc_ids': data.get('ids'),
            'doc_model': data.get('model'),
            'data': data['form'],
        }
        print "===================docargs",docargs
        return self.env['report'].render('report_turnover_by_city.temp_report_turnover_by_city', docargs)
