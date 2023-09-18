odoo.define("pos_hs_code.db", function (require) {
    "use strict";

    var PosDB = require("point_of_sale.DB");
    
    PosDB.include({
        init: function(options) {
            this.product_by_hs_code = {};
            this._super.apply(this, arguments);
        },
        add_products: function(products) {
            this._super(products);

            for (let index = 0; index < products.length; index++) {
                const product = products[index];
                if(product.hs_code) {
                    this.product_by_hs_code[product.hs_code] = product;
                }
            }
        },
        get_product_by_hs_code: function(hs_code) {
            if(this.product_by_hs_code[hs_code]) {
                return this.product_by_hs_code[hs_code];
            } else {
                return undefined;
            }
        },
    })
    return PosDB;
})