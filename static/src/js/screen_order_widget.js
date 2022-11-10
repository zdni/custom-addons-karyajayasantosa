"use strict";
odoo.define('ti_pos_retail.screen_order_widget', function (require) {

    var screens = require('point_of_sale.screens');

    screens.OrderWidget.include({
        remove_event_keyboard: function () {
            if (this.pos.server_version == 10) {
                $('.leftpane').off('keypress', this.keyboard_handler);
                $('.leftpane').off('keydown', this.keyboard_keydown_handler);
            }
            if ([11, 12].indexOf(this.pos.server_version) != -1) {
                $('body').off('keypress', this.keyboard_handler);
                $('body').off('keydown', this.keyboard_keydown_handler);
            }
            window.document.body.removeEventListener('keypress', this.keyboard_handler);
            window.document.body.removeEventListener('keydown', this.keyboard_keydown_handler);
        },
        set_total_gift: function (total_gift) {
            $('.total_gift').html(total_gift);
        },
        set_amount_total: function (amount_total) {
            var amount_total = this.format_currency_no_symbol(amount_total)
            $('.amount_total').html(amount_total);
        },
        set_total_items: function (count) {
            $('.set_total_items').html(count);
        },
        update_summary: function () {
            var self = this
            this._super();
            setTimeout(function () {
                $('input').click(function () {
                    self.remove_event_keyboard();
                });
            }, 100);
            // $('.mode-button').click(function () {
            //     self.change_mode();
            // });
            $('.pay').click(function () {
                self.remove_event_keyboard();
            });
            $('.set-customer').click(function () {
                self.remove_event_keyboard();
            });
            var self = this;
            var selected_order = this.pos.get_order();
            var buttons = this.getParent().action_buttons;
            if (selected_order && buttons) {
                
                this.set_total_items(selected_order.orderlines.length);
                this.set_amount_total(selected_order.get_total_with_tax());
                var promotion_lines = _.filter(selected_order.orderlines.models, function (line) {
                    return line.promotion;
                });
                if (promotion_lines.length > 0) {
                    this.set_total_gift(promotion_lines.length)
                }
            }
        }
    });
});
