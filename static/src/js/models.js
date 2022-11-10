odoo.define("ti_pos_retail.models", function(require) {
    "use strict";
    var models = require("point_of_sale.models");

    var _super_pos_model = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        initialize: function() {
            _super_pos_model.initialize.apply(this, arguments);
        },
        update_discount_by_product: function( discounts ) {
            const self = this;
            if (!(discounts instanceof Array)) discounts = [discounts];

            discounts.forEach(discount => {
                let product_ids = discount.product_ids;
                if (!(product_ids instanceof Array)) product_ids = [product_ids];

                product_ids.forEach(product => {
                    self.db.discount_by_product[product] = {'discount_value': discount.discount_value};
                });
            });
        },
        update_discount_by_product_category: function( discounts ) {
            const self = this;
            if (!(discounts instanceof Array)) discounts = [discounts];

            discounts.forEach(discount => {
                let product_category_ids = discount.product_category_ids;
                if (!(product_category_ids instanceof Array)) product_category_ids = [product_category_ids];

                product_category_ids.forEach(product_category => {
                    self.db.discount_by_product_category[product_category] = {'discount_value': discount.discount_value};
                });
            });
        },
    });

    models.load_fields('pos.order.line', ['promotion','promotion_reason']);

    return models;
});