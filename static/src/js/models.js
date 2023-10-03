odoo.define("deposit_customer.models", function(require) {
    "use strict";
    var models = require("point_of_sale.models");

    models.load_fields('res.partner', ['total_deposit']);
    
    return models;
})