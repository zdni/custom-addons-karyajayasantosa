 # -*- coding: utf-8 -*-
from collections import namedtuple
from datetime import datetime, date, timedelta
from dateutil import relativedelta

from odoo import api, fields, models, _, registry
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from psycopg2 import OperationalError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

import logging

_logger = logging.getLogger(__name__)

class InternalReorder(models.Model):
    _name = "stock.internal.reorder"

    name = fields.Char(
            'Name', copy=False, required=True,
            default=lambda self: self.env['ir.sequence'].next_by_code('stock.internal.reorder'))
    active = fields.Boolean(
            'Active', default=True,
            help="If the active field is set to False, it will allow you to hide the orderpoint without removing it.")
    warehouse_id = fields.Many2one(
            'stock.warehouse', 'Origin Warehouse',
            ondelete="cascade", required=True)
    location_id = fields.Many2one(
            'stock.location', 'Origin Location',
            ondelete="cascade", required=True)

    dest_warehouse_id = fields.Many2one(
            'stock.warehouse', 'Destination Warehouse',
            ondelete="cascade", required=True)
    dest_location_id = fields.Many2one(
            'stock.location', 'Destination Location',
            ondelete="cascade", required=True)

    product_id = fields.Many2one(
            'product.product', 'Product',
            domain=[('type', '=', 'product')], ondelete='cascade', required=True)
    product_tmpl_id = fields.Many2one(
            'product.template', 'Product Template',
            related='product_id.product_tmpl_id',
            help="Technical: used in views")
    product_uom = fields.Many2one(
            'product.uom', 'Product Unit of Measure', related='product_id.uom_id',
            readonly=True, required=True,
            default=lambda self: self._context.get('product_uom', False))
    product_min_qty = fields.Float(
            'Minimum Quantity', digits=dp.get_precision('Product Unit of Measure'), required=True,
            help="When the virtual stock goes below the Min Quantity specified for this field, Odoo generates "
            "a procurement to bring the forecasted quantity to the Max Quantity.")
    product_max_qty = fields.Float(
            'Maximum Quantity', digits=dp.get_precision('Product Unit of Measure'), required=True,
            help="When the virtual stock goes below the Min Quantity, Odoo generates "
            "a procurement to bring the forecasted quantity to the Quantity specified as Max Quantity.")
    qty_multiple = fields.Float(
            'Qty Multiple', digits=dp.get_precision('Product Unit of Measure'),
            default=1, required=True,
            help="The procurement quantity will be rounded up to this multiple.  If it is 0, the exact quantity will be used.")
    company_id = fields.Many2one(
            'res.company', 'Company', required=True,
            default=lambda self: self.env['res.company']._company_default_get('stock.warehouse.orderpoint'))

    _sql_constraints = [
            ('qty_multiple_check', 'CHECK( qty_multiple >= 0 )', 'Qty Multiple must be greater than or equal to zero.'),
    ]

    @api.constrains('product_id')
    def _check_product_uom(self):
        ''' Check if the UoM has the same category as the product standard UoM '''
        if any(orderpoint.product_id.uom_id.category_id != orderpoint.product_uom.category_id for orderpoint in self):
            raise ValidationError(_('You have to select a product unit of measure in the same category than the default unit of measure of the product'))

    @api.onchange('warehouse_id')
    def onchange_warehouse_id(self):
        """ Finds location id for changed warehouse. """
        if self.warehouse_id:
            self.location_id = self.warehouse_id.lot_stock_id.id

    @api.onchange('dest_warehouse_id')
    def onchange_dest_warehouse_id(self):
        """ Finds location id for changed warehouse. """
        if self.dest_warehouse_id:
            self.dest_location_id = self.dest_warehouse_id.lot_stock_id.id

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.product_uom = self.product_id.uom_id.id
            return {'domain':  {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}}
        return {'domain': {'product_uom': []}}

    @api.multi
    def _prepare_stock_picking_values(self, picking_type_id ):
        return {
                'location_id': self.location_id.id,
                'location_dest_id': self.dest_location_id.id,
                'state': 'draft',
                'picking_type_id': picking_type_id.id,
                'min_date': datetime.today()
            }

    @api.multi
    def _prepare_stock_move_values(self, picking_id ):
        return {
                'name': 'Internal Reorder' + self.name,
                # 'company_id': self.company_id.id,
                'product_id': self.product_id.id,
                'stock_in_store': self.product_tmpl_id.stock_in_store,
                'stock_in_warehouse': self.product_tmpl_id.stock_in_warehouse,
                'stock_in_canvas_car': self.product_tmpl_id.stock_in_canvas_car,
                'product_uom_qty': self.product_max_qty,
                'product_uom': self.product_uom.id,
                'location_id': self.location_id.id,
                'location_dest_id': self.dest_location_id.id,
                'picking_id': picking_id.id
            }
            
    @api.multi
    def run(self, autocommit=False):
        # TDE FIXME: avoid browsing everything -> avoid prefetching ?
        for internal_reorder in self:
            # we intentionnaly do the browse under the for loop to avoid caching all ids which would be resource greedy
            # and useless as we'll make a refresh later that will invalidate all the cache (and thus the next iteration
            # will fetch all the ids again)
            try:
                StockPickingTypeSudo = self.env['stock.picking.type'].sudo()
                StockPickingSudo = self.env['stock.picking'].sudo()
                StockMoveSudo = self.env['stock.move'].sudo()
                picking_type = StockPickingTypeSudo.search([ 
                    ("code", '=', 'internal' ), 
                    ("warehouse_id", '=', internal_reorder.warehouse_id.id ),
                    ("default_location_src_id", '=', internal_reorder.location_id.id ),
                    ("default_location_dest_id", '=', internal_reorder.location_id.id ),
                ])

                if picking_type :
                    stock_picking_value = internal_reorder._prepare_stock_picking_values(picking_type[0])
                    stock = StockPickingSudo.search([('state', '=', 'draft')], limit=1, order='id desc, min_date desc')
                    t = date.today()

                    if stock:
                        if stock.min_date:
                            if (t.strftime("%Y-%m-%d") in stock.min_date) and len(stock.move_lines) < 80:
                                stock_picking = stock
                            else:
                                stock_picking = StockPickingSudo.create(stock_picking_value)
                        else:
                            stock_picking = StockPickingSudo.create(stock_picking_value)
                    else:
                        stock_picking = StockPickingSudo.create(stock_picking_value)
                    
                    stock_move = StockMoveSudo.search([
                        ('product_id', '=', self.product_id.id),
                        ('location_id', '=', self.location_id.id),
                        ('location_dest_id', '=', self.dest_location_id.id),
                        ('state', '=', 'draft')
                    ])

                    if not stock_move:
                        stock_move_value = internal_reorder._prepare_stock_move_values( stock_picking )
                        StockMoveSudo.create(stock_move_value)
                    
                if autocommit:
                    self.env.cr.commit()
            except OperationalError:
                if autocommit:
                    self.env.cr.rollback()
                    continue
                else:
                    raise
        return True

    @api.model
    def run_scheduler(self, use_new_cursor=False, company_id=False):

        try:
            if use_new_cursor:
                cr = registry(self._cr.dbname).cursor()
                self = self.with_env(self.env(cr=cr))  # TDE FIXME
            _logger.warning("run_scheduler")
            InternalReorderSudo = self.env['stock.internal.reorder'].sudo()
            StockQuantSudo = self.env['stock.quant'].sudo()
            # Run 
            internal_reorders = InternalReorderSudo.search([])
            for internal_reorder in internal_reorders:
                stock_quants = StockQuantSudo.search([ ("product_id", '=', internal_reorder.product_id.id ), ("location_id", '=', internal_reorder.dest_location_id.id ) ])
                qty_total = sum([ stock_quant.qty for stock_quant in stock_quants ])
                if( qty_total <= internal_reorder.product_min_qty ):

                    internal_reorder.run(autocommit=use_new_cursor)

            self.env['stock.picking'].search([
                ('state', '=', 'draft'), 
                ('location_id', '=', internal_reorders[0].location_id.id), 
                ('location_dest_id', '=', internal_reorders[0].dest_location_id.id), 
                ('move_lines', '=', False)
            ]).unlink()
            
            if use_new_cursor:
                self.env.cr.commit()

        finally:
            if use_new_cursor:
                try:
                    self.env.cr.close()
                except Exception:
                    pass

        return {}
