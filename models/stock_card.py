from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)

class StockCard(models.Model):
    _name = "stock.card"
    
    date			= fields.Datetime("Tanggal")
    description		= fields.Char("Deskripsi")
    information		= fields.Char("Deskripsi")
    loc_id          = fields.Many2one('stock.location', 'Lokasi', required=True)
    location_id		= fields.Many2one('stock.location', 'Lokasi Sumber', required=True)
    location_dest_id= fields.Many2one('stock.location', 'Lokasi Tujuan', required=True)
    picking_id		= fields.Many2one('stock.picking', 'Picking')
    product_id		= fields.Many2one('product.product', 'Produk', required=True)
    qty_start		= fields.Float("Qty Awal")
    qty_in			= fields.Float("Qty Masuk")
    qty_out			= fields.Float("Qty Keluar")
    qty_balance		= fields.Float("Qty Akhir")

    @api.model
    def stock_card(self, product_id):
        product = self.env['product.product'].search([ ('id', '=', product_id) ])
        product_uom = product.uom_id

        # mengambil seluruh stock move untuk product
        moves = self.env['stock.move'].search([
            ("product_id.id", "=", product_id),
            ("has_count", "=", False),
            ("state", "=", "done"),
        ], order="date asc")

        # membuat array untuk warehouse internal location 
        warehouses = []
        warehouses_lost = []
        warehouse_int = self.env['stock.location'].search([
            ('usage', '=', 'internal')
        ])
        warehouse_lost = self.env['stock.location'].search([
            ('usage', '=', 'inventory')
        ]) 
        for warehouse in warehouse_int:
            warehouses.append(warehouse.location_id.name)
        for warehouse in warehouse_lost:
            warehouses_lost.append(warehouse.location_id.name)

        for move in moves:
            stock_cards = self.env['stock.card'].search([
                ('date', '<=', move.date),
                ("product_id.id", "=", product_id),
            ], order="date desc, id desc")

            move.write({ 'has_count': True })
            information = ""
            if move.location_id.location_id.name in warehouses:
                loc_id = move.location_id.id
                description = "Barang Keluar dari " + move.location_id.location_id.name
                stock_card = self.env['stock.card'].search([
                    ('date', '<=', move.date),
                    ("product_id.id", "=", product_id),
                    ("description", "in", ["Barang Keluar dari " + move.location_id.location_id.name, "Barang Masuk ke " + move.location_id.location_id.name])
                ], order="date desc, id desc", limit=1)
                qty_start = stock_card.qty_balance

                if move.picking_id.name:
                    if "/IN/" in move.picking_id.name:
                        information = "Return Penjualan" if "Customers" in move.picking_id.location_id.name  else "Pembelian"
                    if "POS" in move.picking_id.name:
                        information = "Penjualan Kasir"
                    if "/OUT/" in move.picking_id.name:
                        information = "Return Pembelian" if "Vendors" in move.picking_id.location_dest_id.name else "Penjualan"
                    if "/INT/" in move.picking_id.name:
                        information = "Transfer Item dari " + move.location_id.location_id.name + " ke " + move.location_dest_id.location_id.name
                    if "RP" in move.picking_id.name:
                        information = "Produksi"
                else:
                    if move.location_dest_id.location_id.name in warehouses_lost:
                        information = "Stok Opname"
                
                value = self.convert_uom( product_uom, move.product_uom, move.product_uom_qty )
                qty_out = value
                qty_in = 0
                qty_balance = qty_start + (qty_in -  qty_out)
                self.create_stock_card({ 
                    'product_id': move.product_id.id, 'date': move.date, 'information': information, 'description': description, 'loc_id': loc_id,
                    'location_id': move.location_id.id, 'location_dest_id': move.location_dest_id.id,'picking_id': move.picking_id.id,
                    'qty_start': qty_start,'qty_in': qty_in,'qty_out': qty_out,'qty_balance': qty_balance
                })

            if move.location_dest_id.location_id.name in warehouses:
                loc_id = move.location_dest_id.id
                description = "Barang Masuk ke " + move.location_dest_id.location_id.name
                stock_card = self.env['stock.card'].search([
                    ('date', '<=', move.date),
                    ("product_id.id", "=", product_id),
                    ("description", "in", ["Barang Keluar dari " + move.location_dest_id.location_id.name, "Barang Masuk ke " + move.location_dest_id.location_id.name])
                ], order="date desc, id desc", limit=1)
                qty_start = stock_card.qty_balance
                
                if move.picking_id.name:
                    if "/IN/" in move.picking_id.name:
                        information = "Return Penjualan" if "Customers" in move.picking_id.location_id.name  else "Pembelian"
                    if "POS" in move.picking_id.name:
                        information = "Penjualan Kasir"
                    if "WH/OUT" in move.picking_id.name:
                        information = "Return Pembelian" if "Vendors" in move.picking_id.location_dest_id.name else "Penjualan"
                    if "/INT/" in move.picking_id.name:
                        information = "Transfer Item dari " + move.location_id.location_id.name + " ke " + move.location_dest_id.location_id.name
                    if "RP" in move.picking_id.name:
                        information = "Produksi"
                else:
                    information = "Stok Opname"
                
                value = self.convert_uom( product_uom, move.product_uom, move.product_uom_qty )
                qty_in = value
                qty_out = 0
                qty_balance = qty_start + (qty_in -  qty_out)
                self.create_stock_card({ 
                    'product_id': move.product_id.id, 'date': move.date, 'information': information, 'description': description, 'loc_id': loc_id,
                    'location_id': move.location_id.id, 'location_dest_id': move.location_dest_id.id,'picking_id': move.picking_id.id,
                    'qty_start': qty_start,'qty_in': qty_in,'qty_out': qty_out,'qty_balance': qty_balance
                })
            
    @api.model
    def create_stock_card( self, vals ):
        res = super(StockCard, self).create(vals)
        return res

    def convert_uom(self, init, to, value):
        if to.uom_type == 'bigger':
            value = value*to.factor_inv
        if to.uom_type == 'smaller':
            value = value/to.factor
        
        if init.uom_type == 'bigger':
            value = value/init.factor_inv
        if init.uom_type == 'smaller':
            value = value*init.factor
        
        return value