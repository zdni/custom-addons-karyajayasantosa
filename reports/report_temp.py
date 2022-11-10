from odoo import api, models

import logging
_logger = logging.getLogger(__name__)
class ReportBrandSalesTemp(models.AbstractModel):
    _name = 'report.report_brand_sales.report_temp'

    @api.model
    def render_html(self, docids, data=None):
        docargs =  {
            'doc_ids': data.get('ids'),
            'doc_model': data.get('model'),
            'data': data['form'],
            'date': data['date'],
        }
        return self.env['report'].render('report_brand_sales.report_temp', docargs)
