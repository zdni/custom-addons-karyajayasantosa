from odoo import api, models


class LaporanOmsetMarginSalesperson(models.AbstractModel):
    _name = 'report.laporan_omset_margin_salesperson.omset_margin_temp'

    @api.model
    def render_html(self, docids, data=None):
        docargs =  {
            'doc_ids': data.get('ids'),
            'doc_model': data.get('model'),
            'data': data['form'],
            'start_date': data['start_date'],
            'end_date': data['end_date'],
            'visible': data['visible'],
        }
        print "===================docargs",docargs
        return self.env['report'].render('laporan_omset_margin_salesperson.omset_margin_temp', docargs)
