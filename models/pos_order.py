import logging
from datetime import timedelta
from functools import partial

import psycopg2
import pytz

from odoo import api, fields, models, tools, _
from odoo.tools import float_is_zero
from odoo.exceptions import UserError
from odoo.http import request
import odoo.addons.decimal_precision as dp

import logging
_logger = logging.getLogger(__name__)

class PosOrder(models.Model):
    _inherit = "pos.order"

    discount_description = fields.Char('Discount Description')
    has_discount = fields.Boolean('Has Discount')
    percent_discount = fields.Float(string='Discount (%)')
    total_discount = fields.Float(string='Total Discount')

    promotion_ids = fields.Many2many('pos.promotion',
                                     'pos_order_promotion_rel',
                                     'order_id',
                                     'promotion_id',
                                     string='Promotions')

    @api.model
    def _order_fields(self, ui_order):
        process_line = partial(self.env['pos.order.line']._order_line_fields)
        return {
            'name'                  : ui_order['name'],
            'user_id'               : ui_order['user_id'] or False,
            'session_id'            : ui_order['pos_session_id'],
            'lines'                 : [process_line(l) for l in ui_order['lines']] if ui_order['lines'] else False,
            'pos_reference'         : ui_order['name'],
            'partner_id'            : ui_order['partner_id'] or False,
            'date_order'            : ui_order['creation_date'],
            'fiscal_position_id'    : ui_order['fiscal_position_id'],
            'discount_description'  : ui_order['discount_description'] or False,
            'has_discount'          : ui_order['has_discount'] or False,
            'percent_discount'      : ui_order['percent_discount'] or False,
            'total_discount'        : ui_order['total_discount'] or False,
        }

    # def _create_account_move_line(self, session=None, move=None):
    #     def _flatten_tax_and_children(taxes, group_done=None):
    #         children = self.env['account.tax']
    #         if group_done is None:
    #             group_done = set()
    #         for tax in taxes.filtered(lambda t: t.amount_type == 'group'):
    #             if tax.id not in group_done:
    #                 group_done.add(tax.id)
    #                 children |= _flatten_tax_and_children(tax.children_tax_ids, group_done)
    #         return taxes + children

    #     # Tricky, via the workflow, we only have one id in the ids variable
    #     """Create a account move line of order grouped by products or not."""
    #     IrProperty = self.env['ir.property']
    #     ResPartner = self.env['res.partner']

    #     if session and not all(session.id == order.session_id.id for order in self):
    #         raise UserError(_('Selected orders do not have the same session!'))

    #     grouped_data = {}
    #     have_to_group_by = session and session.config_id.group_by or False
    #     rounding_method = session and session.config_id.company_id.tax_calculation_rounding_method

    #     def add_anglosaxon_lines(grouped_data):
    #         Product = self.env['product.product']
    #         Analytic = self.env['account.analytic.account']
    #         for product_key in list(grouped_data.keys()):
    #             if product_key[0] == "product":
    #                 line = grouped_data[product_key][0]
    #                 product = Product.browse(line['product_id'])
    #                 # In the SO part, the entries will be inverted by function compute_invoice_totals
    #                 price_unit = - product._get_anglo_saxon_price_unit()
    #                 account_analytic = Analytic.browse(line.get('analytic_account_id'))
    #                 res = Product._anglo_saxon_sale_move_lines(
    #                     line['name'], product, product.uom_id, line['quantity'], price_unit,
    #                         fiscal_position=order.fiscal_position_id,
    #                         account_analytic=account_analytic)
    #                 if res:
    #                     line1, line2 = res
    #                     line1 = Product._convert_prepared_anglosaxon_line(line1, order.partner_id)
    #                     insert_data('counter_part', {
    #                         'name': line1['name'],
    #                         'account_id': line1['account_id'],
    #                         'credit': line1['credit'] or 0.0,
    #                         'debit': line1['debit'] or 0.0,
    #                         'partner_id': line1['partner_id']

    #                     })

    #                     line2 = Product._convert_prepared_anglosaxon_line(line2, order.partner_id)
    #                     insert_data('counter_part', {
    #                         'name': line2['name'],
    #                         'account_id': line2['account_id'],
    #                         'credit': line2['credit'] or 0.0,
    #                         'debit': line2['debit'] or 0.0,
    #                         'partner_id': line2['partner_id']
    #                     })

    #     for order in self.filtered(lambda o: not o.account_move or o.state == 'paid'):
    #         current_company = order.sale_journal.company_id
    #         account_def = IrProperty.get(
    #             'property_account_receivable_id', 'res.partner')
    #         order_account = order.partner_id.property_account_receivable_id.id or account_def and account_def.id
    #         partner_id = ResPartner._find_accounting_partner(order.partner_id).id or False
    #         if move is None:
    #             # Create an entry for the sale
    #             journal_id = self.env['ir.config_parameter'].sudo().get_param(
    #                 'pos.closing.journal_id_%s' % current_company.id, default=order.sale_journal.id)
    #             move = self._create_account_move(
    #                 order.session_id.start_at, order.name, int(journal_id), order.company_id.id)

    #         def insert_data(data_type, values):
    #             # if have_to_group_by:
    #             values.update({
    #                 'partner_id': partner_id,
    #                 'move_id': move.id,
    #             })

    #             if data_type == 'product':
    #                 key = ('product', values['partner_id'], (values['product_id'], tuple(values['tax_ids'][0][2]), values['name']), values['analytic_account_id'], values['debit'] > 0)
    #             elif data_type == 'tax':
    #                 key = ('tax', values['partner_id'], values['tax_line_id'], values['debit'] > 0)
    #             elif data_type == 'counter_part':
    #                 key = ('counter_part', values['partner_id'], values['account_id'], values['debit'] > 0)
    #             else:
    #                 return

    #             grouped_data.setdefault(key, [])

    #             if have_to_group_by:
    #                 if not grouped_data[key]:
    #                     grouped_data[key].append(values)
    #                 else:
    #                     current_value = grouped_data[key][0]
    #                     current_value['quantity'] = current_value.get('quantity', 0.0) + values.get('quantity', 0.0)
    #                     current_value['credit'] = current_value.get('credit', 0.0) + values.get('credit', 0.0)
    #                     current_value['debit'] = current_value.get('debit', 0.0) + values.get('debit', 0.0)
    #             else:
    #                 grouped_data[key].append(values)

    #         # because of the weird way the pos order is written, we need to make sure there is at least one line,
    #         # because just after the 'for' loop there are references to 'line' and 'income_account' variables (that
    #         # are set inside the for loop)
    #         # TOFIX: a deep refactoring of this method (and class!) is needed
    #         # in order to get rid of this stupid hack
    #         assert order.lines, _('The POS order must have lines when calling this method')
    #         # Create an move for each order line
    #         cur = order.pricelist_id.currency_id
    #         for line in order.lines:
    #             amount = line.price_subtotal

    #             # Search for the income account
    #             if line.product_id.property_account_income_id.id:
    #                 income_account = line.product_id.property_account_income_id.id
    #             elif line.product_id.categ_id.property_account_income_categ_id.id:
    #                 income_account = line.product_id.categ_id.property_account_income_categ_id.id
    #             else:
    #                 raise UserError(_('Please define income '
    #                                   'account for this product: "%s" (id:%d).')
    #                                 % (line.product_id.name, line.product_id.id))

    #             name = line.product_id.name
    #             if line.notice:
    #                 # add discount reason in move
    #                 name = name + ' (' + line.notice + ')'

    #             # Create a move for the line for the order line
    #             # Just like for invoices, a group of taxes must be present on this base line
    #             # As well as its children
    #             base_line_tax_ids = _flatten_tax_and_children(line.tax_ids_after_fiscal_position).filtered(lambda tax: tax.type_tax_use in ['sale', 'none'])
    #             insert_data('product', {
    #                 'name': name,
    #                 'quantity': line.qty,
    #                 'product_id': line.product_id.id,
    #                 'account_id': income_account,
    #                 'analytic_account_id': self._prepare_analytic_account(line),
    #                 'credit': ((amount > 0) and amount) or 0.0,
    #                 'debit': ((amount < 0) and -amount) or 0.0,
    #                 'tax_ids': [(6, 0, base_line_tax_ids.ids)],
    #                 'partner_id': partner_id
    #             })

    #             # Create the tax lines
    #             taxes = line.tax_ids_after_fiscal_position.filtered(lambda t: t.company_id.id == current_company.id)
    #             if not taxes:
    #                 continue
    #             price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
    #             for tax in taxes.compute_all(price, cur, line.qty)['taxes']:
    #                 insert_data('tax', {
    #                     'name': _('Tax') + ' ' + tax['name'],
    #                     'product_id': line.product_id.id,
    #                     'quantity': line.qty,
    #                     'account_id': tax['account_id'] or income_account,
    #                     'credit': ((tax['amount'] > 0) and tax['amount']) or 0.0,
    #                     'debit': ((tax['amount'] < 0) and -tax['amount']) or 0.0,
    #                     'tax_line_id': tax['id'],
    #                     'partner_id': partner_id
    #                 })

    #         # round tax lines per order
    #         if rounding_method == 'round_globally':
    #             for group_key, group_value in grouped_data.iteritems():
    #                 if group_key[0] == 'tax':
    #                     for line in group_value:
    #                         line['credit'] = cur.round(line['credit'])
    #                         line['debit'] = cur.round(line['debit'])

    #         # counterpart
    #         insert_data('counter_part', {
    #             'name': _("Trade Receivables"),  # order.name,
    #             'account_id': order_account,
    #             'credit': ((order.amount_total < 0) and -order.amount_total) or 0.0,
    #             'debit': ((order.amount_total > 0) and order.amount_total) or 0.0,
    #             'partner_id': partner_id
    #         })

    #         order.write({'state': 'done', 'account_move': move.id})

    #     if self and order.company_id.anglo_saxon_accounting:
    #         add_anglosaxon_lines(grouped_data)

    #     all_lines = []
    #     for group_key, group_data in grouped_data.iteritems():
    #         for value in group_data:
    #             all_lines.append((0, 0, value),)
    #     if move:  # In case no order was changed
    #         move.sudo().write({'line_ids': all_lines})
    #         move.sudo().post()
    #     return True

class pos_order_line(models.Model):
    _inherit = "pos.order.line"

    promotion = fields.Boolean('Promotion', readonly=1)
    promotion_reason = fields.Char(string='Promotion reason', readonly=1)
    product_get_promo_id = fields.Many2one('product.product', string='Product Get Promo')
    category_get_promo_id = fields.Many2one('product.category', string='Category Get Promo')