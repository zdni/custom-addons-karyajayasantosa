odoo.define("pos_bank_charge.model", function (require) {
    "use strict";
    
    var models = require('point_of_sale.models');

	var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
            export_for_printing: function () {
            var res = _super_order.export_for_printing.apply(this, arguments);
            res.percent_discount = this.percent_discount;
            res.total_discount = this.total_discount;
            return res;
        },
    });
});