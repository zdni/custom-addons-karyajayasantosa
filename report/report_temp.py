from odoo import api, models

import logging
_logger = logging.getLogger(__name__)
class ReportAccountReceivableAgeTemp(models.AbstractModel):
    _name = 'report.report_account_receivable_age.report_temp'

    @api.model
    def render_html(self, docids, data=None):
        docargs =  {
            'doc_ids': data.get('ids'),
            'doc_model': data.get('model'),
            'data': data['form'],
            'age': data['age'],
            'date': data['date'],
        }
        print "===================docargs",docargs
        _logger.warning(docargs)
        return self.env['report'].render('report_account_receivable_age.report_temp', docargs)
