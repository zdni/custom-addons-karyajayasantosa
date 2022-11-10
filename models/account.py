# -*- coding: utf-8 -*-
##############################################################################
#
#    This module uses OpenERP, Open Source Management Solution Framework.
#    Copyright (C) 2017-Today Sitaram
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)

class AccountReportByCiity(models.TransientModel):
    _name = 'account.account.report'

    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date(string="End Date", required=True)
    city_ids = fields.Many2many("vit.kota", string='Kota', required=False)
    is_fully = fields.Boolean('Tampilkan Customer dengan Tagihan sama dengan 0')

    
    @api.multi
    def print_accounting_report_by_city(self):
        groupby_dict = {}
        is_fully = 0
        if self.is_fully:
            is_fully = 1

        if len(self.city_ids) == 0:
            self.city_ids = self.env['vit.kota'].search([])

        for city in self.city_ids:
            partners = self.env['res.partner'].search([('kota_id.name', '=', city.name)])
                        
            partner_detail = []
            for partner in partners:
                invoices = self.env['account.invoice'].search([ 
                    ('date_invoice', '<=', self.end_date), 
                    ('date_invoice', '>=', self.start_date), 
                    ('state', '=', 'open'), 
                    ('type', '=', 'out_invoice'), 
                    ('partner_id.name', '=', partner.display_name) 
                ],
                order="date_invoice asc")
                partner_temp = []
                partner_invoices = []
                partner_temp.append(partner.display_name) #0
                partner_temp.append(partner.credit_limit) #1
                for invoice in invoices:
                    partner_invoice = []
                    partner_invoice.append(invoice.date_invoice) #0
                    partner_invoice.append(invoice.number) #1
                    partner_invoice.append(invoice.date_due) #2
                    partner_invoice.append(invoice.origin) #3
                    partner_invoice.append(invoice.amount_total_signed ) #4
                    partner_invoice.append(invoice.residual_signed ) #5
                    partner_invoice.append(invoice.user_id.name) #6
                    partner_invoices.append(partner_invoice)

                partner_temp.append(partner_invoices)
                partner_temp.append(partner.risk_total) #3
                
                partner_temp.append(is_fully) #4
                partner_temp.append(partner.risk_invoice_open) #5
                if not is_fully and len(partner_invoices) < 1:
                    continue
                partner_detail.append(partner_temp) #2

            if len(partner_detail) < 1:
                continue
            groupby_dict[city.name] = partner_detail

        datas = {
            'ids': self.ids,
            'model': 'account.account.report',
            'form': groupby_dict,
            'start_date': self.start_date,
            'end_date': self.end_date,

        }
        return self.env['report'].get_action(self,'accounting_report_groupby_city.city_temp', data=datas)

    @api.multi
    def print_accounting_report_by_city_xlsx(self):
        self.ensure_one()
        report_type = 'xlsx'
        return self._export(report_type)
    
    def _prepare_report_trial_balance(self):
        self.ensure_one()
        return {
            'ids': self.ids,
            'model': 'account.account.report',
            'data': groupby_dict,
            'start_date': self.start_date,
            'end_date': self.end_date,
        }

    def _export(self, report_type):
        """Default export is PDF."""
        model = self.env['report_trial_balance_qweb']
        report = model.create(self._prepare_report_trial_balance())
        return report.print_report(report_type)
