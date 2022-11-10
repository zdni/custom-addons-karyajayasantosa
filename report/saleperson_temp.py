from odoo import api, models


class SaleReportCustomerWise(models.AbstractModel):
    _name = 'report.so_report_groupby_customer.so_report_groupby_customer'

    @api.model
    def render_html(self, docids, data=None):
        docargs =  {
            'doc_ids': data.get('ids'),
            'doc_model': data.get('model'),
            'data': data['form'],
            'start_date': data['start_date'],
            'end_date': data['end_date'],
        }
        print "===================docargs",docargs
        return self.env['report'].render('so_report_groupby_customer.so_report_groupby_customer', docargs)
