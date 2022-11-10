odoo.define('pos_discount_template.discount_customer', function (require) {
    "use strict";

    var screens = require('point_of_sale.screens');
	var Model = require('web.DataModel');
    var core = require('web.core');

    var _t = core._t;

    screens.ClientListScreenWidget.include({
        init: function(parent, options) {
            this._super(parent, options);
        },

        show: function() {
            var self = this;
            this._super();
            const order = this.pos.get_order();
            
            this.$('.next').click(function(){
                const discount_product = self.pos.config.disc_product_id;
                if( !discount_product ) {
                    return alert(_t('Invalid Discount Product'));
                }

                const client = order.get_client();
                if( client ) {
                    new Model('pos.discount_customer')
                        .query(['discount_type', 'discount_value', 'partner_ids'])
                        .filter([['status', '=', true], ['partner_ids', '=', client.id]])
                        .all()
                        .then(
                            function(result) {
                                if( result.length ) {
                                    let total_discount = 0;
    
                                    const amount = order.get_total_without_tax();
                                    const discount_type = result[0].discount_type;
                                    const discount_value = result[0].discount_value;
                                    
                                    if( discount_type == 'percent' ) {
                                        total_discount = amount * discount_value / 100 * -1; 
                                        order.set_percent_discount( discount_value );
                                    } else if( discount_type == 'fix' ) {
                                        total_discount = discount_value * -1;
                                    }
    
                                    const product = self.pos.db.get_product_by_id(discount_product[0]);
                                    if ( product ) {
                                        order.set_discount_description( 'Discount By Customer' );
                                        order.set_has_discount( true );
                                        order.set_total_savings( total_discount * -1 );
                                        order.set_total_discount( total_discount * -1 );

                                        order.add_product(product, {
                                            price: total_discount,
                                            extras: {
                                                price_manually_set: true,
                                            },
                                        });
                                        const selected_orderline = order.get_selected_orderline();
                                        selected_orderline.set_skip_check_price( true );
                                    }
                                }
                            }
                        )
                }
            });
        },

        
    });
});