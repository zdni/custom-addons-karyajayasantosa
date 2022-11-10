    odoo.define('pos_promotion.model', function (require) {
        var models = require('point_of_sale.models');
    
        models.load_models([{
                model: 'pos.order.line',
                fields: [
                    'name',
                    'notice',
                    'product_id',
                    'price_unit',
                    'qty',
                    'price_subtotal',
                    'price_subtotal_incl',
                    'discount',
                    'order_id',
                    'promotion',
                    'promotion_reason',
                    'create_uid',
                    'write_date',
                    'create_date',
                ],
                domain: [],
                loaded: function (self, order_lines) {
                    self.db.save_pos_order_line(order_lines);
                }
            },
        ]);
    });
    