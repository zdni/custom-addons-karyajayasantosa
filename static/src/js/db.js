odoo.define("pos_discount_template.db", function(require) {
    "use strict";
    var PosDB = require("point_of_sale.DB");

    PosDB.include({
        init: function(options) {
            this.discount_by_product = {};
            this.discount_by_product_category = {};
            this._super.apply(this, arguments);
        },
        get_discount_by_product: function(id) {
            return this.discount_by_product[id];
        },
        get_discount_by_product_category: function(id) {
            return this.discount_by_product_category[id];
        },
    });
    return PosDB;
});