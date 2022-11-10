odoo.define('ti_pos_retail.order', function (require) {
    
    var models = require('point_of_sale.models');

    models.Order = models.Order.extend({
        validate_payment_order: function () {
            if (this && this.orderlines.models.length == 0) {
                this.pos.gui.show_screen('products');
                return this.pos.gui.show_popup('dialog', {
                    title: 'Warning',
                    body: 'Your order lines is blank'
                })
            }
            if (this.remaining_point && this.remaining_point < 0) {
                this.pos.gui.show_screen('products');
                return this.pos.gui.show_popup('dialog', {
                    title: 'Warning',
                    body: 'You could not applied redeem point bigger than client point',
                });
            }
            this.validate_promotion();
        },
    });
});
