from odoo import api, fields, models

class PosDetails(models.TransientModel):
    _inherit = 'pos.details.wizard'

    @api.multi
    def print_pos_details_report_xlsx(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'pos.details.wizard'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        if len(datas['ids']) > 1:
            raise except_orm('Warning', 'Selection of multiple record is not allowed')
        else:
            return {'type': 'ir.actions.report.xml',
                'report_name': 'pos_details_report_xlsx',
                'datas': datas,
            }