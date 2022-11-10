odoo.define("pos_check_price.models", function(require) {
    "use strict";
    var models = require("point_of_sale.models");
    // var Model = require("web.Model");

    var _super_pos_model = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        initialize: function() {
            _super_pos_model.initialize.apply(this, arguments);
        },
        update_standard_price_by_product_id: function( products ) {
            const self = this;
            if (!(products instanceof Array)) products = [products];

            products.forEach(product => {
                self.db.standard_price_by_product_id[product.id] = {'standard_price': product.standard_price, 'list_price': product.list_price};
            });
        }
    });

    models.load_models({
        model:  'product.product',
        fields: ['standard_price', 'list_price'],
        domain: [['sale_ok','=',true],['available_in_pos','=',true]],
        context: function(self){ return { pricelist: self.pricelist.id, display_default_code: false }; },
        loaded: function(self, products){
            self.update_standard_price_by_product_id( products );
        },
    });
   
    return models;
});