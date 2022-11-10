from odoo import api, fields, models, tools, _

import logging
_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = "product.template"

    type_rule_store = fields.Selection([
        ('int', _('Internal Transfer')),
        ('rfq', _('RFQ')),
    ], string='Tipe Dokumen', required=True, default='int')
    stock_min_in_store = fields.Integer('Stok Minimum Toko', required=True, default=0)
    stock_max_in_store = fields.Integer('Stok Maksimum Toko', required=True, default=0)

    stock_min_in_warehouse = fields.Integer('Stok Minimum Gudang', required=True, default=0)
    stock_max_in_warehouse = fields.Integer('Stok Maksimum Gudang', required=True, default=0)

    @api.model_cr
    def init(self):
        docs_rfq = self.env['stock.warehouse.orderpoint'].search([])
        for doc in docs_rfq:
            product = self.env['product.template'].search([
                ('id', '=', doc.product_id.id),
            ])
            product.write({
                'warehouse_ids': doc.location_ids,
                'min_stock': doc.product_min_qty,
                'max_stock': doc.product_max_qty,
            })
            if doc.warehouse_id.name == 'Toko TAS':
                for product_ in product:
                    product_.type_rule_store = 'rfq'
                    product_.stock_min_in_store = doc.product_min_qty
                    product_.stock_max_in_store = doc.product_max_qty

            if doc.warehouse_id.name == 'Gudang TAS':
                for product_ in product:
                    product_.stock_min_in_warehouse = doc.product_min_qty
                    product_.stock_max_in_warehouse = doc.product_max_qty            

        docs_int = self.env['stock.internal.reorder'].search([
            ('dest_warehouse_id.name', '=', 'Toko TAS'),
        ])
        for doc in docs_int:
            product = self.env['product.template'].search([
                ('id', '=', doc.product_id.id ),
            ])
            for product_ in product:
                product_.stock_min_in_store = doc.product_min_qty
                product_.stock_max_in_store = doc.product_max_qty

    @api.multi
    def create_doc_rfq(self):
        warehouse = self.env['stock.warehouse'].search([
            ('name', '=', 'Gudang TAS')
        ])
        location_warehouse = self.env['stock.location'].search([
            ('name', '=', 'Stock'),
            ('location_id.name', '=', 'GDTAS'),
        ])

        self.env['stock.warehouse.orderpoint'].create({
            'warehouse_id': warehouse.id,
            'location_id': location_warehouse.id,
            'product_id': self._origin.id,
            'product_uom': self.uom_id.id,
            'product_min_qty': self.stock_min_in_store,
            'product_max_qty': self.stock_max_in_store,
            'qty_multiple': 1.0,
            'lead_days': 1,
            'lead_type': 'supplier',
        })
        self.env.cr.commit()

    @api.multi
    def create_doc_int(self):
        warehouse_store = self.env['stock.warehouse'].search([
            ('name', '=', 'Toko TAS')
        ])
        warehouse = self.env['stock.warehouse'].search([
            ('name', '=', 'Gudang TAS')
        ])
        location_warehouse = self.env['stock.location'].search([
            ('name', '=', 'Stock'),
            ('location_id.name', '=', 'GDTAS'),
        ])
        dest_location_id = self.env['stock.location'].search([
            ('name', '=', 'TAS: Transit Location'),
        ])
        self.env['stock.internal.reorder'].create({
            'product_id': self._origin.id,
            'product_uom': self.uom_id.id,
            'warehouse_id': warehouse.id,
            'location_id': location_warehouse.id,
            'dest_warehouse_id': warehouse_store.id,
            'dest_location_id': dest_location_id.id,
            'product_min_qty': self.stock_min_in_store,
            'product_max_qty': self.stock_max_in_store,
            'qty_multiple': 1.0,
        })
        self.env.cr.commit()

    @api.multi
    @api.onchange('stock_min_in_store', 'stock_max_in_store')
    def create_rule_store(self):
        if self.type_rule_store == 'rfq':
            doc = self.env['stock.warehouse.orderpoint'].search([
                ('product_id.id', '=', self._origin.id)
            ])
        if self.type_rule_store == 'int':
            doc = self.env['stock.internal.reorder'].search([
                ('product_id.id', '=', self._origin.id)
            ])

        if doc:
            doc.write({
                'product_min_qty': self.stock_min_in_store, 
                'product_max_qty': self.stock_max_in_store, 
            })
        else:
            if self.stock_min_in_store:
                if self.type_rule_store == 'int':
                    self.create_doc_int()
                    
                if self.type_rule_store == 'rfq':
                    self.create_doc_rfq()

    @api.multi
    @api.onchange('stock_min_in_warehouse', 'stock_max_in_warehouse')
    def create_rule_warehouse(self):
        doc = self.env['stock.warehouse.orderpoint'].search([
            ('product_id.id', '=', self._origin.id)
        ])

        if doc:
            doc.write({
                'product_min_qty': self.stock_min_in_warehouse, 
                'product_max_qty': self.stock_max_in_warehouse, 
            })
        else:
            if self.stock_min_in_warehouse:
                self.create_doc_rfq()