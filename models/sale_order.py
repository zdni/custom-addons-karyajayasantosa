 # -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = "sale.order"


    location_id = fields.Many2one(
            'stock.location', 'Origin Location', related="warehouse_id.lot_stock_id",
            ondelete="cascade", required=True)

    @api.onchange('warehouse_id')
    def _onchange_warehouse_id(self):
        """ Finds location id for changed warehouse. """
        super(SaleOrder, self)._onchange_warehouse_id()
        _logger.warning( self.location_id )
        
        if self.warehouse_id:
            self.location_id = self.warehouse_id.lot_stock_id.id


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    location_id = fields.Many2one(
            'stock.location', 'Stock Location', related="order_id.location_id", readonly=True, store=True ) 
    
    product_stocks = fields.Float( string='Stok Produk Pada Gudang Yang Di Pilih = ', copy=True, readonly=True, default=0, store=True )
    # product_stocks = fields.One2many('product.stock', inverse_name='order_line_id', string='Product Stocks', copy=True, readonly=True )

    # def set_location(self):
    #     self.location_id = self.order_id.location_id

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        super(SaleOrderLine, self).product_id_change()
        StockQuantSudo = self.env['stock.quant'].sudo()
        _logger.warning( self.location_id )
        if( self.product_id ) :
            stock_quants = StockQuantSudo.search([ ("product_id", '=', self.product_id.id ), ("location_id", '=', self.location_id.id ) ])
            stock_qty_total = sum([ stock_quant.qty for stock_quant in stock_quants ])
            _logger.warning( stock_qty_total )
            self.product_stocks = stock_qty_total

            # product_stocks = []
            # ProductStockSudo = self.env['product.stock'].sudo()
            # st_values = {
            #     'product_id': self.product_id.id,
            #     'location_id': self.location_id.id,
            #     'stock_qty': stock_qty_total
            # }
            # product_stocks.append(ProductStockSudo.create(st_values).id)
            # self.product_stocks = product_stocks

    # @api.onchange('product_uom', 'product_uom_qty')
    # def product_uom_change(self):
    #     super(SaleOrderLine, self).product_uom_change()
    #     StockQuantSudo = self.env['stock.quant'].sudo()
    #     _logger.warning( "product_uom_change" )
    #     _logger.warning( "product_uom_change" )

    #     if( self.location_id and self.product_id ) :
    #         qty = self.product_uom_qty
    #         stock_quants = StockQuantSudo.search([ ("product_id", '=', self.product_id.id ), ("location_id", '=', self.location_id.id ) ])
    #         stock_qty_total = sum([ stock_quant.qty for stock_quant in stock_quants ])

    #         _logger.warning( qty )
    #         _logger.warning( stock_qty_total )
    #         if( stock_qty_total < qty ):
    #             self.product_uom_qty = 0
    #             raise UserError(_("not enough stock in selected warehouse") )
