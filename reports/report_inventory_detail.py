from odoo import api, models

import logging
_logger = logging.getLogger(__name__)
class ReportInventoryDetail(models.AbstractModel):
    _name = 'report.report_inventory.report_inventory_detail'

    @api.model
    def render_html(self, docids, data=None):
        docargs =  {
            'doc_ids': data.get('ids'),
            'doc_model': data.get('model'),
            'data': data['form'],
            'date': data['date'],
        }
        return self.env['report'].render('report_inventory.report_inventory_detail', docargs)
