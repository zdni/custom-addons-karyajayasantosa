odoo.define('pos_discount_template.global_discount', function (require) {
    "use strict";

    var gui = require('point_of_sale.gui');
    var screens = require('point_of_sale.screens');
	var PopupWidget = require('point_of_sale.popups');
    var core = require('web.core');

    var _t = core._t;

    var PosGlobalDiscountPopup = PopupWidget.extend({
        template: 'PosGlobalDiscountPopup',
        show: function(options) {
            this._super(options);
            var self = this;

			self.renderElement();
	    	$('.discount_input').focus();
        },
        click_confirm: function() {
            var self = this;
            var order = this.pos.get_order();
            var discount_input = $('.discount_input');
            const discount_product = this.pos.config.disc_product_id;
            
            if( !discount_product ) {
                return alert(_t('Invalid Discount Product'));
            }
            if(discount_input.val() && $.isNumeric(discount_input.val()) && Number(discount_input.val()) > 0 && Number(discount_input.val()) <= 100) {
                const amount = order.get_total_without_tax();
                const total_discount = amount * discount_input.val() / 100 * -1; 
                
                const product = this.pos.db.get_product_by_id(discount_product[0]);
                if (total_discount < 0 && product) {
                    order.set_discount_description( 'Discount Global' );
                    order.set_has_discount( true );
                    order.set_percent_discount( discount_input.val() );
                    order.set_total_discount( total_discount * -1 );
                    order.set_total_savings( total_discount * -1 );

                    order.add_product(product, {
                        price: total_discount,
                        extras: {
                            price_manually_set: true,
                        },
                    });
                    const selected_orderline = order.get_selected_orderline();
                    selected_orderline.set_skip_check_price( true );
                }
            } else {
                alert(_t("Invalid Input"))
            }
            this.gui.close_popup();
        },
        renderElement: function() {
            this._super();
            var self = this;
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
                if( order.get_total_without_tax() < this.pos.config.min_order_disc_global ) {
                    return this.gui.show_popup('error', {
                        'title': _t('Error'),
                        'body': _t('Total Order not reach minimum order to get global discount'),
                    });
                }
                if( this.pos.config.lock_discount == true ) {
                    this.gui.show_popup('password', {
                        'title': _t('Password ?'),
                        confirm: function (pw) {
                            const string_pin = this.pos.config.string_pin
                            const array_string_pin = string_pin.split('|')
                            
                            let access_accept = false;
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
});