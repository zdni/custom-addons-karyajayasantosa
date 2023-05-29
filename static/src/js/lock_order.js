odoo.define('auth_order_of_stock.lock_order', function (require) {
    "use strict"

    var models = require('point_of_sale.models')
    var core = require('web.core')
    var _t = core._t
    
    var _super_order = models.Order.prototype
    models.Order = models.Order.extend({
        add_product: function (product, options) {
            const self = this
            if (product['qty_available'] <= 0 && self.pos.config['allow_order_out_of_stock'] == true) {
                if(self.pos.config.lock_order == true) {
                    self.pos.gui.show_popup('password', {
                        'title': _t('Password ?'),
                        confirm: function (pw) {
                            const string_pin = self.pos.config.string_pin_order
                            const array_string_pin = string_pin.split('|')
                            
                            let access_accept = false
                            array_string_pin.forEach(pin => {
                                if( pin.slice(2) == pw.toString() ) { access_accept = true }
                            })
                            
                            if ( !access_accept ) {
                                return self.pos.gui.show_popup('error', {
                                    'title': _t('Error'),
                                    'body': _t('Incorrect password. Please try again'),
                                })
                            } else {
                                return _super_order.add_product.call(this, product, options)
                            }
                        },
                    })
                } else {
                    return _super_order.add_product.call(this, product, options)
                }
            } else {
                return _super_order.add_product.call(this, product, options)
            }
        },
    })

})