from datetime import datetime, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class SchedulePricelistProduct(models.Model):
    _name = "schedule.pricelist.product"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Schedule Pricelist Product"
    _order = "start_date desc"

    name = fields.Char('Name', required=True)
    start_date = fields.Datetime('Start Date', required=True)
    end_date = fields.Datetime('End Date', required=True)
    line_ids = fields.One2many('schedule.pricelist.product.line', 'pricelist_id', string='Product Line')
    # is_running = fields.Boolean('Is Running', default=False)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
        # ('done', 'Expired'),
    ], string='Status', readonly=True, index=True, default='draft', copy=False)

    def cron_update_schedule_pricelist_product(self):
        _logger.warning( 'start' )
        now = datetime.now() + timedelta(hours=8)
        date = now.strftime("%Y-%m-%d")

        start_date = date + " 00:00:00"
        end_date = date + " 23:59:59"

        documents = self.env['schedule.pricelist.product'].search([
            ('state', '=', 'draft'),
            ('start_date', '>=', start_date),
            ('start_date', '<=', end_date),
        ], order='start_date asc')
        for document in documents:
            for line in document.line_ids:
                product_tmpl_id = line.product_id.product_tmpl_id.id
                ProductTemplate = self.env['product.template'].sudo().search([
                    ('id', '=', product_tmpl_id)
                ], limit=1)
                if ProductTemplate:
                    ProductTemplate.write({
                        'list_price': line.selling_price,
                        'standard_price_pricelist': line.purchase_price
                    })
            document.write({
                'state': 'done'
            })
        _logger.warning( 'done' )


    def action_run_document(self):
        for record in self:
            for line in record.line_ids:
                product_tmpl_id = line.product_id.product_tmpl_id.id
                ProductTemplate = self.env['product.template'].sudo().search([
                    ('id', '=', product_tmpl_id)
                ], limit=1)
                if ProductTemplate:
                    ProductTemplate.write({
                        'list_price': line.selling_price,
                        'standard_price_pricelist': line.purchase_price
                    })
            record.write({
                'state': 'done'
            })

class SchedulePricelistProductLine(models.Model):
    _name = "schedule.pricelist.product.line"

    # product_ids = fields.Many2many('product.product', string='Product')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    uom_id = fields.Many2one('product.uom', string='UoM', required=True, readonly=True)
    purchase_price = fields.Float('Purchase Price', required=True)
    selling_price = fields.Float('Selling Price', required=True)
    pricelist_id = fields.Many2one('schedule.pricelist.product', string='Pricelist', ondelete="cascade")

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id.product_tmpl_id:
            # self.uom_id = self.product_id.product_tmpl_id.uom_id.id
            self.uom_id = self.product_id.product_tmpl_id.uom_po_id.id