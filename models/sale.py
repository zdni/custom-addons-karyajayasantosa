from odoo import api, fields, models, exceptions, _
import logging

_logger = logging.getLogger(__name__)
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    @api.onchange('price_unit')
    def _check_price(self):
        if(self.price_unit < self.product_id.product_tmpl_id.standard_price):
            _logger.warning('change')
            # raise exceptions.Warning('This leave is allowed only for saudi citizens')
            return {
                'warning': {
                    'title': 'Warning!',
                    'message': 'ANDA MENJUAL PRODUK INI DIBAWAH HARGA MODAL!!!'
                }
            }
        
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    @api.onchange('order_line')
    def _check_validate_order_line(self):
        for line in self.order_line:
            if(line.price_unit < line.product_id.product_tmpl_id.standard_price):
                return {
                    'warning': {
                        'title': 'Warning!',
                        'message': 'ANDA MENJUAL PRODUK ' + line.product_id.name +' INI DIBAWAH HARGA MODAL!!!'
                    }
                }