from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare
from odoo import api, fields, models, _

import logging
_logger = logging.getLogger(__name__)

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    discount_view = fields.Selection([('after', 'After Tax')], string='Discount Type')
    discount_type = fields.Selection([('fixed', 'Fixed'), ('percentage', 'Percentage')], string='Discount Method')                                     
    discount_value = fields.Float(string='Discount Value', store=True)
    discounted_amount = fields.Float(compute='disc_amount', string='Discounted Amount', store=True, readonly=True)

    @api.onchange('purchase_id')
    def purchase_order_change(self):
        if not self.purchase_id:
            return {}
        self.discount_view = self.purchase_id.discount_view
        self.discount_type = self.purchase_id.discount_type
        self.discount_value = self.purchase_id.discount_value
        invoice = super(AccountInvoice, self).purchase_order_change()
        return invoice


    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'currency_id', 'company_id', 'date_invoice', 'discount_type', 'discount_value')
    def _compute_amount(self):
        res = super(AccountInvoice, self)._compute_amount()
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
        self.amount_tax = sum(line.amount for line in self.tax_line_ids)
        if self.discount_view == 'after':
            if self.discount_type == 'fixed':
                self.amount_total = self.amount_untaxed + self.amount_tax - self.discount_value
            elif self.discount_type == 'percentage':
                if self.discount_value < 100:
                    amount_to_dis = (self.amount_untaxed + self.amount_tax) * (self.discount_value / 100)
                    self.amount_total = (self.amount_untaxed + self.amount_tax) - amount_to_dis
                else:
                    raise UserError(_('Discount percentage should not be greater than 100.'))
            else:
                self.amount_total = self.amount_untaxed + self.amount_tax
        
        else:
            self.amount_total = self.amount_untaxed + self.amount_tax        
        amount_total_company_signed = self.amount_total
        amount_untaxed_signed = self.amount_untaxed
        if self.currency_id and self.currency_id != self.company_id.currency_id:
            currency_id = self.currency_id.with_context(date=self.date_invoice)
            amount_total_company_signed = currency_id.compute(self.amount_total, self.company_id.currency_id)
            amount_untaxed_signed = currency_id.compute(self.amount_untaxed, self.company_id.currency_id)
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        self.amount_total_company_signed = amount_total_company_signed * sign
        self.amount_total_signed = self.amount_total * sign
        self.amount_untaxed_signed = amount_untaxed_signed * sign
        return res

    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'currency_id', 'company_id', 'date_invoice', 'discount_type', 'discount_value')
    def disc_amount(self):
        if self.discount_view == 'after':
            if self.discount_type == 'fixed':
                self.discounted_amount = self.discount_value
            elif self.discount_type == 'percentage':
                amount_to_dis = (self.amount_untaxed + self.amount_tax) * (self.discount_value / 100)
                self.discounted_amount = amount_to_dis
            else:
                self.discounted_amount = 0
        
        else:
            self.discounted_amount = 0


    @api.one
    @api.depends(
        'state', 'currency_id', 'invoice_line_ids.price_subtotal',
        'move_id.line_ids.amount_residual',
        'move_id.line_ids.currency_id')
    def _compute_residual(self):
        residual = 0.0
        residual_company_signed = 0.0
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        for line in self.sudo().move_id.line_ids:
            if line.account_id.internal_type in ('receivable', 'payable'):
                residual_company_signed += line.amount_residual
                if line.currency_id == self.currency_id:
                    residual += line.amount_residual_currency if line.currency_id else line.amount_residual
                else:
                    from_currency = (line.currency_id and line.currency_id.with_context(date=line.date)) or line.company_id.currency_id.with_context(date=line.date)
                    residual += from_currency.compute(line.amount_residual, self.currency_id)

        self.residual_company_signed = abs(residual_company_signed) * sign
        self.residual_signed = abs(residual) * sign
        self.residual = abs(residual)

        # self.residual_company_signed = (abs(residual_company_signed) - self.discounted_amount) * sign
        # self.residual_signed = (abs(residual) - self.discounted_amount) * sign
        # self.residual = abs(residual) - self.discounted_amount

        digits_rounding_precision = self.currency_id.rounding
        if float_is_zero(self.residual, precision_rounding=digits_rounding_precision):
            self.reconciled = True
        else:
            self.reconciled = False

    @api.multi
    def action_move_create(self):
        """ Creates invoice related analytics and financial move lines """
        account_move = self.env['account.move']

        discount_value = (0, 0, {})
        for inv in self:
            if not inv.journal_id.sequence_id:
                raise UserError(_('Please define sequence on the journal related to this invoice.'))
            if not inv.invoice_line_ids:
                raise UserError(_('Please create some invoice lines.'))
            if inv.move_id:
                continue

            ctx = dict(self._context, lang=inv.partner_id.lang)

            if not inv.date_invoice:
                inv.with_context(ctx).write({'date_invoice': fields.Date.context_today(self)})
            company_currency = inv.company_id.currency_id

            # create move lines (one per invoice line + eventual taxes and analytic lines)
            iml = inv.invoice_line_move_line_get()
            iml += inv.tax_line_move_line_get()

            diff_currency = inv.currency_id != company_currency
            # create one move line for the total and possibly adjust the other lines amount
            total, total_currency, iml = inv.with_context(ctx).compute_invoice_totals(company_currency, iml)

            name = inv.name or '/'
            if inv.payment_term_id:
                totlines = inv.with_context(ctx).payment_term_id.with_context(currency_id=company_currency.id).compute(total, inv.date_invoice)[0]
                res_amount_currency = total_currency
                ctx['date'] = inv._get_currency_rate_date()
                for i, t in enumerate(totlines):
                    if inv.currency_id != company_currency:
                        amount_currency = company_currency.with_context(ctx).compute(t[1], inv.currency_id)
                    else:
                        amount_currency = False

                    # last line: add the diff
                    res_amount_currency -= amount_currency or 0
                    if i + 1 == len(totlines):
                        amount_currency += res_amount_currency

                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': t[1],
                        'account_id': inv.account_id.id,
                        'date_maturity': t[0],
                        'amount_currency': diff_currency and amount_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'invoice_id': inv.id
                    })
            else:
                iml.append({
                    'type': 'dest',
                    'name': name,
                    'price': total,
                    'account_id': inv.account_id.id,
                    'date_maturity': inv.date_due,
                    'amount_currency': diff_currency and total_currency,
                    'currency_id': diff_currency and inv.currency_id.id,
                    'invoice_id': inv.id
                })

            part = self.env['res.partner']._find_accounting_partner(inv.partner_id)
            line = [(0, 0, self.line_get_convert(l, part.id)) for l in iml]
            line = inv.group_lines(iml, line)

            journal = inv.journal_id.with_context(ctx)
            line = inv.finalize_invoice_move_lines(line)
    
            date = inv.date or inv.date_invoice

            if inv.discounted_amount > 0:
                res_company = self.env['res.company'].search([
                    ('id', '=', self.env.user.company_id.id)
                ])
                account_payable = self.env['ir.property'].search([
                    ('name', '=', 'property_account_payable_id'),
                ])
                account_id = int( account_payable.value_reference.split(',')[1] )
                # change value credit all
                for l in line:
                    if l[2]['account_id'] == account_id:
                        l[2]['credit'] = l[2]['credit'] - inv.discounted_amount

                # add line discount
                line = [ (0, 0, {
                    'account_id': res_company.discount_product.property_account_income_id.id,
                    'amount_currency': 0,
                    'analytic_account_id': False,
                    'analytic_line_ids': [],
                    'analytic_tag_ids': False,
                    'blocked': False,
                    'credit': inv.discounted_amount,
                    'currency_id': False,
                    'date_maturity': inv.date_due,
                    'debit': False,
                    'invoice_id': inv.id,
                    'move_id': inv.move_id.id,
                    'name': res_company.discount_product.name,
                    'partner_id': inv.partner_id.id,
                    'product_id': res_company.discount_product.id,
                    'product_uom_id': res_company.discount_product.uom_id.id,
                    'quantity': 1.0,
                    'tax_line_id': False,
                    'tax_ids': False,
                }) ] + line
                
            move_vals = {
                'ref': inv.reference,
                'line_ids': line,
                'journal_id': journal.id,
                'date': date,
                'narration': inv.comment,
            }
       
            ctx['company_id'] = inv.company_id.id
            ctx['invoice'] = inv
            ctx_nolang = ctx.copy()
            ctx_nolang.pop('lang', None)
            move = account_move.with_context(ctx_nolang).create(move_vals)
            # Pass invoice in context in method post: used if you want to get the same
            # account move reference when creating the same invoice after a cancelled one:
            move.post()
            # make the invoice point to that move
            vals = {
                'move_id': move.id,
                'date': date,
                'move_name': move.name,
            }
            inv.with_context(ctx).write(vals)
        return super(AccountInvoice, self).action_move_create()