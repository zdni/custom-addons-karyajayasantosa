odoo.define('auth_order_of_stock.lock_order', function (require) {
    "use strict"

    var models = require('point_of_sale.models')
    var core = require('web.core')
    var _t = core._t
    
    var _super_order = models.Order.prototype
    models.Order = models.Order.extend({
        initialize: function() {
            _super_order.initialize.apply(this,arguments)
            this.pass_check_allow_order_out_of_stock = this.pass_check_allow_order_out_of_stock || false
        },
        export_as_JSON: function(){
            var json = _super_order.export_as_JSON.apply(this,arguments)
            json.pass_check_allow_order_out_of_stock = this.pass_check_allow_order_out_of_stock
            return json
        },
        init_from_JSON: function(json){
            _super_order.init_from_JSON.apply(this,arguments)
            this.pass_check_allow_order_out_of_stock = json.pass_check_allow_order_out_of_stock
        },
        export_for_printing: function () {
            var json = _super_order.export_for_printing.apply(this, arguments)
            
            json.pass_check_allow_order_out_of_stock = this.get_pass_check_allow_order_out_of_stock()
            return json
        },
        set_pass_check_allow_order_out_of_stock: function(val){
            this.pass_check_allow_order_out_of_stock = val
            this.trigger('change',this)
        },
        get_pass_check_allow_order_out_of_stock: function(){
            return this.pass_check_allow_order_out_of_stock
        },
        add_product: function (product, options) {
            const self = this
            if (product['type'] != 'consu' && product['type'] != 'service') {
                if (product['qty_available'] <= 0 && self.pos.config['allow_order_out_of_stock'] == true) {
                    if(self.pos.config.lock_order == true && self.pass_check_allow_order_out_of_stock == false) {
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
                                    self.set_pass_check_allow_order_out_of_stock(true)
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

    var _super_order_line = models.Orderline.prototype
    models.Orderline = models.Orderline.extend({
        set_quantity: function (quantity) {
            const self = this
            console.log('self orderline: ', self)
            if (this.pos.the_first_load == false && quantity != 'remove' && this.product['qty_available'] < quantity && this.pos.config['allow_order_out_of_stock'] == true) {
                // if( !['consu','service'].includes( this.product['type'] ) ) {
                if( this.product['type'] != 'consu' && this.product['type'] != 'service' ) {
                    if(self.pos.config.lock_order == true && self.order.pass_check_allow_order_out_of_stock == false) {
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
                                    return _super_order_line.set_quantity.call(self, quantity)
                                }
                            },
                        })
                    } else {
                        return _super_order_line.set_quantity.call(self, quantity)
                    }
                } else {
                    return _super_order_line.set_quantity.call(self, quantity)
                }
            } else {
                return _super_order_line.set_quantity.call(self, quantity)
            }
        }
    })
})