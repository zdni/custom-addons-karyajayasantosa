odoo.define('check_so_under_cost.screens', function (require) {
    "use strict";
    
    var models = require('point_of_sale.models');
    var Model = require("web.Model");
    var screens = require('point_of_sale.screens');

    models.load_fields('product.product',['type','standard_price','list_price']);

    var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        initialize: function() {
            _super_orderline.initialize.apply(this,arguments);
            this.skip_check_price = this.skip_check_price || false;
        },
        init_from_JSON: function(json) {
            _super_orderline.init_from_JSON.apply(this,arguments);
            this.skip_check_price = json.skip_check_price;
        },
        export_as_JSON: function() {
            var json = _super_orderline.export_as_JSON.apply(this,arguments);
            json.skip_check_price = this.skip_check_price;
            return json;
        },
        set_skip_check_price: function(skip) {
            this.skip_check_price = skip;
            this.trigger('change', this);
        },
        get_skip_check_price: function() {
            return this.skip_check_price;
        },
    });
    
    screens.ActionpadWidget.include({
        renderElement: function() {
            const self = this;
            this._super();

            this.$('.pay').click(async function(){
                const order = self.pos.get_order();
                const orderlines = order.get_orderlines();
                const stock_location = self.pos.config.stock_location_id;
                let products = '';
                
                for (let index = 0; index < orderlines.length; index++) {
                    const orderline = orderlines[index];
                    
                    if(orderline.skip_check_price) continue;

                    const product = orderline.product;
                    if(['service'].includes( product.type )) continue;

                    const orderline_price = orderline.price;
                    // const product_price = self.pos.db.get_standard_price_by_product_id( product.id );
                    
                    await new Promise(resolve => {
                        resolve(
                            new Model('stock.quant')
                                .query(['id', 'product_id', 'cost'])
                                .filter([['product_id', '=', product.id], ['location_id', '=', stock_location[0]]])
                                .limit(1)
                                .all()
                                .then(
                                    function(stock_quant) {
                                        if(product.qty_available === 0) return
                                        if( orderline_price < stock_quant[0].cost ) {
                                            products += product.display_name + ', ';
                                            orderline.set_unit_price( product.list_price );
                                        }
                                    }
                                )
                        );
                    });

                    // if( orderline_price < product_price.standard_price ) {
                    // if( orderline_price < product.standard_price ) {
                    //     products += product.display_name + ', ';
                    //     // orderline.set_unit_price( product_price.list_price );
                    //     orderline.set_unit_price( product.list_price );
                    // }
                }
                if( products ) {
                    self.gui.back();
                    return self.pos.gui.show_popup('error', {
                        title: '!!! Warning !!!',
                        body: 'Anda menjual produk: ' + products + ' dibawah harga modal!!!'
                    });
                }
            });
        },
    });
    
});