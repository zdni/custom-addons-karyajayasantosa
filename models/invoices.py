from odoo import api, exceptions, fields, models, _
import logging
from datetime import date, timedelta

_logger = logging.getLogger(__name__)
class Settlement(models.Model):
    _name = "sale.commission.settlement"

    name = fields.Char('Name')
    total_settled = fields.Float(compute="_compute_total_settled", readonly=True, store=True)
    total_invoice = fields.Float('Total Invoice')
    total = fields.Float(compute="_compute_total", readonly=True, store=True)
    date_from = fields.Date(string="From")
    date_to = fields.Date(string="To")
    agent = fields.Many2one(
        comodel_name="res.partner", domain="[('agent', '=', True)]")
    lines = fields.One2many(
        comodel_name="sale.commission.settlement.line",
        inverse_name="settlement", string="Settlement lines", readonly=True)
    state = fields.Selection(
        selection=[("draft", "Draft"),
                   ("validated", "Validated"),
                   ("cancel", "Canceled")], string="State",
        readonly=True, default="draft")
    invoice = fields.Many2one(
        comodel_name="account.invoice", string="Generated invoice",
        readonly=True)
    commission = fields.Many2one(
        comodel_name="sale.commission")

    @api.depends('lines', 'total_settled')
    def _compute_total(self):
        for record in self:
            if record.commission.commission_type == "fixed":
                record.total = (record.total_settled*record.commission.fix_qty)/100
            elif record.commission.commission_type == "section":
                for section in record.commission.sections:
                    if section.amount_from < record.total_settled < section.amount_to:
                        record.total = (record.total_settled*section.percent)/100
    
    @api.depends('lines')
    def _compute_total_settled(self):
        for record in self:
            total_ = 0
            total = 0
            for invoice in record.lines:
                for line in invoice.invoice.invoice_line_ids:
                    total_ += line.price_subtotal
                    record.commission = invoice.invoice.commission.id
                    if not line.product_id.commission_free:
                        total += line.price_subtotal
            record.total_invoice = total_
            _logger.warning(record.total_invoice)
            record.total_settled = total
    
    def action_validated(self):
        if any(x.state != 'draft' for x in self):
            raise exceptions.Warning(
                _('Cannot va;idated an settlement when it canceled.'))
        self.write({'state': 'validated'})
        for line in self.lines:
            line.invoice.write({'settled': True})

    def action_cancel(self):
        if any(x.state != 'draft' for x in self):
            raise exceptions.Warning(
                _('Cannot cancel an settlement when it validated.'))
        self.write({'state': 'cancel'})

class SettlementLines(models.Model):
    _name = "sale.commission.settlement.line"

    settlement = fields.Many2one(
        "sale.commission.settlement",
        readonly=True,
        ondelete="cascade",
        required=True,
    )
    invoice = fields.Many2one(
        comodel_name='account.invoice', store=True, string="Invoice")
    total_invoice = fields.Float(readonly=True, store=True)
    date = fields.Date(store=True)