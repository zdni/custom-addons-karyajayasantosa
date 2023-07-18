odoo.define('auth_order_of_stock.lock_order', function (require) {
    "use strict"

    var models = require('point_of_sale.models')
    var core = require('web.core')
    var _t = core._t
    
    var _super_order = models.Order.prototype
    models.Order = models.Order.extend({
        add_product: function (product, options) {
            const self = this
            if (product['type'] != 'consu' && product['type'] != 'service') {
                if (product['qty_available'] <= 0 && self.pos.config['allow_order_out_of_stock'] == true) {
                    if(self.pos.config.lock_order == true) {
                        self.pos.gui.show_popup('password', {
                            'title': _t('Password ?'),
                            confirm: function (pw) {
                                const string_pin = self.pos.config.string_pin_order
                                const array_string_pin = string_pin.split('|')
                                
                                let access_accept = false
                                array_string_pin.forEach(pin => {
                                    if(pin.length > 0) {
                                        if( pin.slice(3) === pw.toString() ) { access_accept = true }
                                    }
                                })
                                
                                if ( !access_accept ) {
                                    return self.pos.gui.show_popup('error', {
                                        'title': _t('Error'),
                                        'body': _t('Incorrect password. Please try again'),
                                    })
                                } else {
                                    return _super_order.add_product.call(self, product, options)
                                }
                            },
                        })
                    } else {
                        return _super_order.add_product.call(self, product, options)
                    }
                } else {
                    return _super_order.add_product.call(self, product, options)
                }
            } else {
                return _super_order.add_product.call(self, product, options)
            }
        },
    })

    var _super_order_line = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        set_quantity: function (quantity) {
            const self = this
            if (this.pos.the_first_load == false && quantity != 'remove' && this.product['qty_available'] < quantity && this.pos.config['allow_order_out_of_stock'] == true) {
                // if( !['consu','service'].includes( this.product['type'] ) ) {
                if( this.product['type'] != 'consu' && this.product['type'] != 'service' ) {
                    if(self.pos.config.lock_order == true) {
                        self.pos.gui.show_popup('password', {
                            'title': _t('Password ?'),
                            confirm: function (pw) {
                                const string_pin = self.pos.config.string_pin_order
                                const array_string_pin = string_pin.split('|')
                                
                                let access_accept = false
                                array_string_pin.forEach(pin => {
                                    if(pin.length > 0) {
                                        console.log('pin: ', pin)
                                        if( pin.slice(3) === pw.toString() ) { access_accept = true }
                                    }
                                })
                                
                                if ( !access_accept ) {
                                    return self.pos.gui.show_popup('error', {
                                        'title': _t('Error'),
                                        'body': _t('Incorrect password. Please try again'),
                                    })
                                } else {
                                    return _super_order_line.set_quantity.call(self, quantity);
                                }
                            },
                        })
                    } else {
                        return _super_order_line.set_quantity.call(self, quantity);
                    }
                } else {
                    return _super_order_line.set_quantity.call(self, quantity);
                }
            } else {
                return _super_order_line.set_quantity.call(self, quantity);
            }
        }
    });
})