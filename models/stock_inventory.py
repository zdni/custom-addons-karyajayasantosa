from odoo import api, fields, models

import logging
_logger = logging.getLogger(__name__)

class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    @api.multi
    def print_report_xlsx(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'stock.inventory'
        datas['form'] = self.read()[0]
        
        _logger.warning(datas)
        
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'report_inv_adj_xlsx',
            'datas': datas,
        }