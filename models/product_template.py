from odoo import api, fields, models, tools, _

import logging
_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = "product.template"

    type_doc = fields.Selection([
        ('int', _('Internal Transfer')),
        ('rfq', _('RFQ')),
    ], string='Tipe Dokumen', required=True, default='int')

    location_ids = fields.Many2many('stock.location', string='Location')
    min_stock = fields.Float('Minimum Stock', required=True, default=0)
    max_stock = fields.Float('Maximum Stock', required=True, default=0)

    @api.multi
    def create_doc_reordering_rule(self):
        _logger.warning('create_doc_reordering_rule')
        res_company = self.env['res.company'].search([
            ('id', '=', self.env.user.company_id.id)
        ])
        stock_warehouse_id = res_company.stock_warehouse.id
        location_warehouse_id = res_company.location_warehouse.id

        self.env['stock.warehouse.orderpoint'].sudo().create({
            'product_id': self._origin.id,
            'location_ids': self.location_ids,
            'warehouse_id': stock_warehouse_id,
            'product_uom': self.uom_id.id,
            'location_id': location_warehouse_id,
            'product_min_qty': self.min_stock,
            'product_max_qty': self.max_stock,
            'qty_multiple': 1.0,
            'lead_days': 1,
            'lead_type': 'supplier',
        })
        self.env.cr.commit()

    @api.multi
    def create_doc_int_reorder_rule(self):
        _logger.warning('create_doc_int_reorder_rule')
        res_company = self.env['res.company'].search([
            ('id', '=', self.env.user.company_id.id)
        ])
        stock_store_id = res_company.stock_store.id                 #toko
        stock_warehouse_id = res_company.stock_warehouse.id         #gudang
        location_warehouse_id = res_company.location_warehouse.id   #location gudang
        location_transit_id = res_company.location_transit.id       #transit

        self.env['stock.internal.reorder'].create({
            'product_id': self._origin.id,
            'product_uom': self.uom_id.id,
            'warehouse_id': stock_warehouse_id,
            'location_id': location_warehouse_id,
            'dest_warehouse_id': stock_store_id,
            'dest_location_id': location_transit_id,
            'product_min_qty': self.min_stock,
            'product_max_qty': self.max_stock,
            'qty_multiple': 1.0,
        })
        self.env.cr.commit()

    @api.multi
    @api.onchange('min_stock', 'max_stock', 'location_ids', 'type_doc')
    def rule_doc_reordering(self):
        _logger.warning('rule_doc_reordering')
        if self.type_doc == 'rfq':
            doc = self.env['stock.warehouse.orderpoint'].search([
                ('product_id.id', '=', self._origin.id)
            ]).sudo()
        if self.type_doc == 'int':
            doc = self.env['stock.internal.reorder'].search([
                ('product_id.id', '=', self._origin.id)
            ]).sudo()
        
        if doc:
            doc.write({
                'product_min_qty'   : self.min_stock, 
                'product_max_qty'   : self.max_stock,   
            })
            if self.type_doc == 'rfq':
                doc.location_ids = self.location_ids
        
        else:
            if self.type_doc == 'rfq':
                if self.min_stock > 0 and self.max_stock > 0:
                    self.create_doc_reordering_rule()
            if self.type_doc == 'int':
                if self.min_stock > 0 and self.max_stock > 0:
                    self.create_doc_int_reorder_rule()

    # cron to check and related the document reordering to shorcut reordering in product
    def _cron_check_doc_reorder(self):
        _logger.warning('_cron_check_doc_reorder')
        res_company = self.env['res.company'].search([
            ('id', '=', self.env.user.company_id.id)
        ])
        stock_store_id = res_company.stock_store.id                 #toko

        docs_rfq = self.env['stock.warehouse.orderpoint'].search([])
        for doc in docs_rfq:
            doc.product_id.type_doc        = 'rfq'
            doc.product_id.location_ids    = doc.location_ids
            doc.product_id.min_stock       = doc.product_min_qty
            doc.product_id.max_stock       = doc.product_max_qty

        docs_int = self.env['stock.internal.reorder'].search([
            ('dest_warehouse_id.name', '=', 'Toko TAS'),
        ])
        for doc in docs_int:
            doc.product_id.location_ids    = [res_company.location_store.id]
            doc.product_id.min_stock       = doc.product_min_qty
            doc.product_id.max_stock       = doc.product_max_qty