odoo.define('pos_global_discount.global_discount', function (require) {
    "use strict";

    var gui = require('point_of_sale.gui');
	var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
	var PopupWidget = require('point_of_sale.popups');
	var Model = require('web.DataModel');
    var core = require('web.core');
	var utils = require('web.utils');

    var round_pr = utils.round_precision;

    var QWeb = core.qweb;
    var _t = core._t;

    var PosGlobalDiscountPopup = PopupWidget.extend({
        template: 'PosGlobalDiscountPopup',
        show: function(options) {
            var self = this;
            this._super(options);

			self.renderElement();
	    	$('.discount_input').focus();
        },
        click_confirm: function() {
            var self = this;
            var order = this.pos.get_order();
            var discount_input = $('.discount_input');
            const discount_product = this.pos.config.discount_global_product_id;
            
            if( !discount_product ) {
                return alert(_t('Invalid Discount Product'));
            }
            if(discount_input.val() && $.isNumeric(discount_input.val()) && Number(discount_input.val()) > 0 && Number(discount_input.val()) <= 100) {
                const amount = order.get_total_without_tax();
                const total_discount = amount * discount_input.val() / 100 * -1; 
                
                const product = this.pos.db.get_product_by_id(discount_product[0]);
                if (total_discount < 0 && product) {
                    order.set_has_discount( true );
                    order.set_percent_discount( discount_input.val() );

                    order.add_product(product, {
                        price: total_discount,
                        extras: {
                            price_manually_set: true,
                        },
                    });
                }
            } else {
                alert(_t("Invalid Input"))
            }
            this.gui.close_popup();
        },
        renderElement: function() {
            var self = this;
            this._super();
            var order = this.pos.get_order();

            if(self.el.querySelector('.discount_input')) {
                var total_discount_earned = $('.total_discount_earned')

                self.el.querySelector('.discount_input').addEventListener('keyup', function(e){
                    if($.isNumeric( $(this).val() )) {
                        var amount = order.get_total_without_tax() * $(this).val() / 100;
                        total_discount_earned.text( self.format_currency(amount) );
                        
                        if(amount > (order.get_due() || order.get_total_without_tax())) {
                            alert('Diskon melebihi total belanjaan');
                            $(this).val(0);
                            total_discount_earned.text('0.00');
                        }
                    }
                });
            }
        }
    });
    gui.define_popup({name:'pos_global_discount', widget: PosGlobalDiscountPopup});

    var GlobalDiscountButton = screens.ActionButtonWidget.extend({
        template: "PosGlobalDiscountButton",
        button_click: function() {
			var order = this.pos.get_order();
            if(order.get_orderlines().length) {
                if( this.pos.config.lock_discount == true ) {
                    this.gui.show_popup('password', {
                        'title': _t('Password ?'),
                        confirm: function (pw) {
                            const string_pin = this.pos.config.string_pin
                            const array_string_pin = string_pin.split('|')
                            
                            let access_accept = false
                            array_string_pin.forEach(pin => {
                                if( pin.slice(2) == pw.toString() ) { access_accept = true }
                            });

                            if ( !access_accept ) {
                                this.gui.show_popup('error', {
                                    'title': _t('Error'),
                                    'body': _t('Incorrect password. Please try again'),
                                });
                            } else {
                                return this.gui.show_popup('pos_global_discount');
                            }
                        },
                    });
                } else {
                    return this.gui.show_popup('pos_global_discount');
                }
            }
        }
    });
    screens.define_action_button({ name: 'global_discount', widget: GlobalDiscountButton});

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function(attributes, options) {
            _super_order.initialize.apply(this, arguments);
            this.set({ percent_discount: 0.00, has_discount: false });
        },
        set_percent_discount: function(val) {
            this.set('percent_discount', val);
        },
        get_percent_discount: function() {
            return this.get('percent_discount') || 0.00;
        },
        set_has_discount: function(val) {
            this.set('has_discount', val);
        },
        get_has_discount: function() {
            return this.get('has_discount');
        },
        remove_orderline: function( line ){
            if(line.get_product().display_name == this.pos.config.discount_global_product_id[1]) {
                this.set_percent_discount( 0 );
                this.set_has_discount( false );
            }
            _super_order.remove_orderline.apply(this, arguments);
        },
        export_as_JSON: function() {
            var order = _super_order.export_as_JSON.call(this);
            var _order = this.pos.get_order();
            if( _order ) {
                var orderlines = _order.get_orderlines();
                if( orderlines ) {
                    for (let index = 0; index < orderlines.length; index++) {
                        const orderline = orderlines[index];
                        if( orderline.get_product().display_name == this.pos.config.discount_global_product_id[1] ) {
                            var discount = orderline.get_price_without_tax();
                            var total = _order.get_total_without_tax() - discount;
                            var percent_discount = (discount*-100)/total
                            this.set_percent_discount( percent_discount );
                            this.set_has_discount( true );
                        }
                    }
                }
            }
            var new_val = {
                percent_discount: this.get_percent_discount(),
                has_discount: this.get_has_discount(),
            }
            $.extend(order, new_val);

            return order;
        },
        export_for_printing: function() {
            var receipt = _super_order.export_for_printing.call(this);
            var _order = this.pos.get_order();
            if( _order ) {
                var orderlines = _order.get_orderlines();
                if( orderlines ) {
                    for (let index = 0; index < orderlines.length; index++) {
                        const orderline = orderlines[index];
                        if( orderline.get_product().display_name == this.pos.config.discount_global_product_id[1] ) {
                            var discount = orderline.get_price_without_tax();
                            var total = _order.get_total_without_tax() - discount;
                            var percent_discount = (discount*-100)/total
                            this.set_percent_discount( percent_discount );
                            console.log( 'discount', discount )
                            this.set_has_discount( true );
                        }
                    }
                }
            }
            var new_val = {
                percent_discount: this.get_percent_discount(),
                has_discount: this.get_has_discount(),
            }
            $.extend(receipt, new_val);
            return receipt;
        },
    });
});