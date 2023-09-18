odoo.define("pos_hs_code.models", function(require) {
    "use strict";
    var models = require("point_of_sale.models");

    models.load_fields('product.product', ['hs_code']);
    
    return models;
})