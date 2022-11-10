odoo.define("pos_check_price.db", function(require) {
    "use strict";
    var PosDB = require("point_of_sale.DB");

    PosDB.include({
        init: function(options) {
            this.standard_price_by_product_id = {};
            this._super.apply(this, arguments);
        },
        get_standard_price_by_product_id: function(id) {
            return this.standard_price_by_product_id[id];
        }
    });
    return PosDB;
});