odoo.define("pos_picking_note.model", function (require) {
    "use strict";
    
    var models = require('point_of_sale.models');

    var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        export_for_printing: function () {
            var res = _super_orderline.export_for_printing.apply(this, arguments);
            res.picking_note = this.picking_note;
            res.qty_picking = this.qty_picking;
            res.qty_picking_str = this.qty_picking_str;
            return res;
        },
    });
});