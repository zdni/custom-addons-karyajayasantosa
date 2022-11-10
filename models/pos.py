
from odoo import api, fields, models
import logging


_logger = logging.getLogger(__name__)

class PointOfSalePosReport(models.TransientModel):
    _name = 'point_of_sale.pos.report'

    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date(string="End Date", required=True)
    user_ids = fields.Many2many('res.users', string="Salesperson")

    @api.multi
    def print_salesperson_vise_report(self):
        # return
        _logger.warning( "print_salesperson_vise_report" )
        groupby_dict = {}
        for user in self.user_ids:
            user_pos_sessions = {}
            pos_sessions = self.env['pos.session'].search([ ('user_id', '=', user.id), ('start_at', '>=', self.start_date), ('start_at', '<=', self.end_date), ('state', '=', 'closed' ) ], order="start_at asc")
            _logger.warning( pos_sessions )

            groupby_dict[user.name] = pos_sessions

        final_dict = {}
        for user in groupby_dict.keys():
            temp_pos_sessions = []
            for pos_session in groupby_dict[user]:
                temp_pos_session = {}
                temp_pos_session['name'] = pos_session.name

                temp_pos_session['bank_statements'] = []
                for statement in pos_session.statement_ids:
                    temp_statement = {}
                    temp_statement['journal_name'] = statement.journal_id.name
                    temp_statement['balance_end'] = statement.balance_end

                    temp_pos_session['bank_statements'].append(temp_statement)


                temp_pos_session['orders'] = []
                for order in pos_session.order_ids:
                    _logger.warning( order.name )
                    temp_order = {}
                    temp_order['name'] = order.name
                    temp_order['date_order'] = order.date_order
                    # temp_order['partner_name'] = order.partner_id.name if order.partner_id else "UMUM"
                    temp_order['amount_total'] = order.amount_total
                    temp_order['orderlines'] = []

                    for order_line in order.lines:
                        temp_order_line = {}
                        temp_order_line['name'] = order_line.name
                        temp_order_line['product_name'] = order_line.product_id.name
                        temp_order_line['qty'] = order_line.qty
                        temp_order_line['price_unit'] = order_line.price_unit
                        temp_order_line['discount'] = order_line.discount
                        temp_order_line['price_subtotal_incl'] = order_line.price_subtotal_incl

                        temp_order['orderlines'].append(temp_order_line)

                    temp_pos_session['orders'].append(temp_order)

                temp_pos_sessions.append(temp_pos_session)
            final_dict[user] = temp_pos_sessions

        datas = {
            'ids': self.ids,
            'model': 'point_of_sale.pos.report',
            'form': final_dict,
            'start_date': self.start_date,
            'end_date': self.end_date,
        }
        # return
        return self.env['report'].get_action(self,'pos_report_saleperson_groupby.pos_temp', data=datas)
       