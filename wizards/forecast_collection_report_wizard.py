from odoo import api, fields, models, _
from odoo.exceptions import except_orm

import logging
_logger = logging.getLogger(__name__)

class ForecastCollectionReportWizard(models.TransientModel):
    _name = "forecast.collection.report"

    start_date = fields.Date(string='Tanggal Awal', required=True)
    end_date = fields.Date(string='Tanggal Akhir', required=True)
    city_ids = fields.Many2many("vit.kota", string='Kota')

    @api.multi
    def generate_excel(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'forecast.collection.report'
        datas['form'] = self.read()[0]

        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        
        if len(datas['ids']) > 1:
            raise except_orm('Warning', 'Selection of multiple record is not allowed')
        else:
            return {'type': 'ir.actions.report.xml',
                'report_name': 'forecast_collection_report_xlsx',
                'datas': datas,
            }