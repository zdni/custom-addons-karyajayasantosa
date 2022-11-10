from odoo import fields, models, api

import odoo.addons.decimal_precision as dp

import logging
_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = "product.template"

    standard_price_pricelist = fields.Float('Cost', readonly=True)
    standard_price = fields.Float(
        'Cost + Shipping Cost', compute='_compute_standard_price',
        inverse='_set_standard_price', search='_search_standard_price',
        digits=dp.get_precision('Product Price'), groups="base.group_user",
        help="Cost of the product, in the default unit of measure of the product.")