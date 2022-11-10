odoo.define('pos_promotion.database', function (require) {
    var db = require('point_of_sale.DB');

    db.include({
        init: function (options) {
            this._super(options);
            this.order_line_by_id = {};
            this.pos_order_lines = [];
            this.lines_by_order_id = {};
        },
        save_pos_order_line: function (lines) { // save order line from backend
            if (this.pos_order_lines) {
                this.pos_order_lines = lines;
            } else {
                this.pos_order_lines = this.pos_order_lines.concat(lines);
            }
            for (var i = 0; i < lines.length; i++) {
                this.order_line_by_id[lines[i]['id']] = lines[i];
                if (!this.lines_by_order_id[lines[i].order_id[0]]) {
                    this.lines_by_order_id[lines[i].order_id[0]] = [lines[i]]
                } else {
                    this.lines_by_order_id[lines[i].order_id[0]].push(lines[i])
                }
            }
        },
    });
});
