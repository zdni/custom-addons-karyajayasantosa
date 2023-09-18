odoo.define('pos_hs_code.screens', function(require) {
    "use strict";

    var screens = require('point_of_sale.screens');

    screens.ProductCategoriesWidget.include({
        init: function(parent, options) {
            this._super(parent, options);
        },

        perform_search: function(category, query, buy_result) {
            this._super(category, query, buy_result);
            
            var products;
            if(query) {
                products = this.pos.db.get_product_by_hs_code(query);
                if(products) {
                    this.pos.get_order().add_product(products);
                    this.clear_search();
                }
            }
        }
    })
})