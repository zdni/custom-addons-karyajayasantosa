odoo.define('pos_global_discount.global_discount', function (require) {
    "use strict";

	var models = require('point_of_sale.models');
    
    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function() {
            _super_order.initialize.apply(this,arguments);
            
            this.discount_description = this.discount_description || "";
            this.has_discount = this.has_discount || false;
            this.percent_discount = this.percent_discount || 0.00;
            this.total_discount = this.total_discount || 0.00;
            this.save_to_db();

        },
        export_as_JSON: function() {
            var json = _super_order.export_as_JSON.apply(this,arguments);
            json.discount_description = this.discount_description;
            json.has_discount = this.has_discount;
            json.percent_discount = this.percent_discount;
            json.total_discount = this.total_discount;
            return json;
        },
        init_from_JSON: function(json) {
            _super_order.init_from_JSON.apply(this,arguments);
            this.discount_description = json.discount_description;
            this.has_discount = json.has_discount;
            this.percent_discount = json.percent_discount;
            this.total_discount = json.total_discount;
        },
        export_for_printing: function() {
            var json = _super_order.export_for_printing.apply(this,arguments);
            json.discount_description = this.get_discount_description();
            json.has_discount = this.get_has_discount();
            json.percent_discount = this.get_percent_discount();
            json.total_discount = this.get_total_discount();
            return json;
        },
        set_discount_description: function(val) {
            this.discount_description = val;
            this.trigger('change');
        },
        get_discount_description: function() {
            return this.discount_description;
        },
        set_has_discount: function(val) {
            this.has_discount = val;
            this.trigger('change');
        },
        get_has_discount: function() {
            return this.has_discount;
        },
        set_percent_discount: function(val) {
            this.percent_discount = val;
            this.trigger('change');
        },
        get_percent_discount: function() {
            return this.percent_discount;
        },
        set_total_discount: function(val) {
            this.total_discount = val;
            this.set_total_savings( val );
            this.trigger('change');
        },
        get_total_discount: function() {
            return this.total_discount;
        },
        remove_orderline: function( line ){
            if(line.get_product().display_name == this.pos.config.disc_product_id[1]) {
                this.set_discount_description( '' );
                this.set_has_discount( false );
                this.set_percent_discount( 0 );
                this.set_total_discount( 0 );
            }
            _super_order.remove_orderline.apply(this, arguments);
        },
    });
});