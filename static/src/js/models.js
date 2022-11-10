odoo.define("pos_total_savings.models", function(require) {
    "use strict";
    var models = require("point_of_sale.models");

    models.load_fields('pos.order', ['total_savings']);

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function() {
            _super_order.initialize.apply(this,arguments);
            this.total_savings = this.total_savings || 0.00;
        },
        export_as_JSON: function(){
            var json = _super_order.export_as_JSON.apply(this,arguments);
            json.total_savings = this.total_savings;
            return json;
        },
        init_from_JSON: function(json){
            _super_order.init_from_JSON.apply(this,arguments);
            this.total_savings = json.total_savings;
        },
        export_for_printing: function () {
            var json = _super_order.export_for_printing.apply(this, arguments);
            
            let total_savings = 0.00;
            const order = this.pos.get_order();
            if( order ) {
                const orderlines = order.get_orderlines();
                orderlines.forEach(orderline => {
                    total_savings += parseFloat( orderline.get_saving() );
                });
                total_savings += parseFloat( order.get_total_savings() );
            }
            json.total_savings = total_savings;
            return json;
        },
        set_total_savings: function(total_savings){
            this.total_savings = total_savings;
            this.trigger('change',this);
        },
        get_total_savings: function(){
            return this.total_savings;
        },
    });

    var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        initialize: function() {
            _super_orderline.initialize.apply(this,arguments);
            this.saving = this.saving || 0.00;
        },
        export_as_JSON: function(){
            var json = _super_orderline.export_as_JSON.apply(this,arguments);
            json.saving = this.saving;
            return json;
        },
        init_from_JSON: function(json){
            _super_orderline.init_from_JSON.apply(this,arguments);
            this.saving = json.saving;
        },
        export_for_printing: function () {
            var json = _super_orderline.export_for_printing.apply(this, arguments);
            json.saving = this.get_saving();
            return json;
        },
        set_saving: function(saving){
            this.saving = saving;
            this.trigger('change',this);
        },
        get_saving: function(){
            return this.saving;
        },
        set_discount: function(discount) {
            _super_orderline.set_discount.apply(this, arguments);
            this.set_saving_for_orderline();  
        },
        set_quantity: function(quantity) {
            _super_orderline.set_quantity.apply(this, arguments);
            this.set_saving_for_orderline();
        },
        set_unit_price: function(price) {
            _super_orderline.set_unit_price.apply(this, arguments);
            this.set_saving_for_orderline();
        },
        set_saving_for_orderline: function() {
            const total_savings = this.get_unit_price() * (this.get_discount() / 100.0) * this.get_quantity();
            this.set_saving( total_savings );
        }
    });
});