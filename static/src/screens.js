odoo.define('check_so_under_cost.screens', function (require) {
    "use strict";
    
    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var Model = require("web.Model");
    var core = require('web.core');
    var _t = core._t;
    
    screens.OrderWidget.include({
        orderline_add: function(){
            var self = this;
            this._super();
            var order = self.pos.get_order();
            var orderlines = order.orderlines.models

            if(orderlines.length){
                var products_id = [];
                for (let index = 0; index < orderlines.length; index++) {
                    var orderline = orderlines[index];
                    var product = orderline.product;
                    products_id.push(product.id)
                }

                new Model('product.template')
                    .query(['id', 'name', 'standard_price', 'total_one_'])
                    .filter([['id', 'in', products_id]])
                    .all()
                    .then(
                        function(result){
                            // console.log('result: ', result)
                            var messages = '';
                            for (let index = 0; index < result.length; index++) {
                                var indexIn = products_id.indexOf(result[index].id)
                                
                                var price = orderline.order.orderlines.models[indexIn].price;
                                var discount = orderline.order.orderlines.models[indexIn].discount;
                                var product_tmp = result[index];

                                price = price - (price*discount/100)
                                
                                if(price < product_tmp.standard_price) {
                                    messages +=  product_tmp.name + ', '
                                    
                                    var total_one_ = product_tmp.total_one_ 
                                    orderline.order.orderlines.models[indexIn].set_unit_price(total_one_)
                                }
                            }

                            if(messages != ''){
                                return self.pos.gui.show_popup('error', {
                                    title: '!!! Warning !!!',
                                    body: 'Anda menjual produk: ' + messages + ' dibawah harga modal!!!'
                                });
                            }
                        }
                    )
            }
        },

    });

    screens.ActionpadWidget.include({
        renderElement: function() {
            var self = this;
            this._super();
            this.$('.pay').click(function(){
                var order = self.pos.get_order();
                var orderlines = order.orderlines.models

                if(orderlines.length){
                    var products_id = [];
                    for (let index = 0; index < orderlines.length; index++) {
                        var orderline = orderlines[index];
                        var product = orderline.product;
                        products_id.push(product.id)
                    }

                    new Model('product.template')
                        .query(['name', 'standard_price'])
                        .filter([['id', 'in', products_id]])
                        .all()
                        .then(
                            function(result){
                                var messages = '';
                                for (let index = 0; index < result.length; index++) {
                                    var indexIn = products_id.indexOf(result[index].id)
                                    
                                    var price = orderline.order.orderlines.models[indexIn].price;
                                    var discount = orderline.order.orderlines.models[indexIn].discount;
                                    var product_tmp = result[index];
                                    
                                    price = price - (price*discount/100)

                                    if(price < product_tmp.standard_price) {
                                        self.gui.back();
                                        messages +=  product_tmp.name + ', '
                                        
                                        orderline.order.orderlines.models[indexIn].set_unit_price(orderline.order.orderlines.models[indexIn].product.list_price)
                                    }
                                }

                                if(messages != ''){
                                    return self.pos.gui.show_popup('error', {
                                        title: '!!! Warning !!!',
                                        body: 'Anda menjual produk: ' + messages + ' dibawah harga modal!!!'
                                    });
                                }
                            }
                        )
                }
            });
        }
    })
    
});