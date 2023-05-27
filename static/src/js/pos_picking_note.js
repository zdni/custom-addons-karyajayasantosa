odoo.define("pos_picking_note.pos_picking_note", function (require) {
    "use strict";
    var gui = require('point_of_sale.gui');
    var screens = require('point_of_sale.screens');
	var PopupWidget = require('point_of_sale.popups');
    var pos_model = require('point_of_sale.models');var core = require('web.core');

    var _t = core._t;

    var Mode = Object.freeze({ INSERT: 1, NORMAL: 2, POPUP: 3 })
    
    var _super_orderline = pos_model.Orderline.prototype;
    pos_model.load_fields('pos.order.line',['picking_note', 'qty_picking', 'qty_picking_str']);

    pos_model.Orderline = pos_model.Orderline.extend({
        initialize: function() {
            _super_orderline.initialize.apply(this,arguments);
            // _super_orderline.initialize.call(this,attr,options);
            this.picking_note = this.picking_note || "";
            this.qty_picking = this.qty_picking || 0;
            this.qty_picking_str = this.qty_picking_str || "";
        },
        set_picking_note: function(picking_note){
            this.picking_note = picking_note;
            this.trigger('change',this);
        },
        get_picking_note: function(){
            return this.picking_note;
        },
        set_qty_picking: function(qty_picking, qty_picking_str){
            this.qty_picking = qty_picking;
            this.qty_picking_str = qty_picking_str;
            this.trigger('change',this);
        },
        get_qty_picking: function(){
            return this.qty_picking;
        },
        get_qty_picking_str: function(){
            return this.qty_picking_str;
        },
        can_be_merged_with: function(orderline) {
            if (orderline.get_picking_note() !== this.get_picking_note()) {
                return false;
            } else {
                return _super_orderline.can_be_merged_with.apply(this,arguments);
            }
        },
        clone: function(){
            var orderline = _super_orderline.clone.call(this);
            orderline.picking_note = this.picking_note;
            orderline.qty_picking = this.qty_picking;
            orderline.qty_picking_str = this.qty_picking_str;
            return orderline;
        },
        export_as_JSON: function(){
            var json = _super_orderline.export_as_JSON.apply(this,arguments);
            json.picking_note = this.picking_note;
            json.qty_picking = this.qty_picking;
            json.qty_picking_str = this.qty_picking_str;
            return json;
        },
        init_from_JSON: function(json){
            _super_orderline.init_from_JSON.apply(this,arguments);
            this.picking_note = json.picking_note;
            this.qty_picking = json.qty_picking;
            this.qty_picking_str = json.qty_picking_str;
        },
    });

    var _super_order = pos_model.Order.prototype;
    pos_model.load_fields('pos.order','picking_address');
    
    pos_model.Order = pos_model.Order.extend({
        initialize: function() {
            _super_order.initialize.apply(this,arguments);
            this.picking_address = this.picking_address || "";
        },
        export_as_JSON: function(){
            var json = _super_order.export_as_JSON.apply(this,arguments);
            json.picking_address = this.picking_address;
            return json;
        },
        init_from_JSON: function(json){
            _super_order.init_from_JSON.apply(this,arguments);
            this.picking_address = json.picking_address;
        },
        export_for_printing: function () {
            var json = _super_order.export_for_printing.apply(this, arguments);
            json.picking_address = this.get_picking_address();
            return json;
        },
        set_picking_address: function(picking_address){
            this.picking_address = picking_address;
            this.trigger('change',this);
        },
        get_picking_address: function(){
            return this.picking_address;
        },
        clone: function(){
            var order = _super_order.clone.call(this);
            order.picking_address = this.picking_address;
            return order;
        },
    });

    var PosPickingNotePopup = PopupWidget.extend({
        template: 'PosPickingNotePopup',
        show: function(options) {
            var self = this;
            this._super(options);

			self.renderElement();
            $('#orderline-table').children()[1].children[0].children[0].children[0].focus();
        },
        click_confirm: function() {
            var self = this;
            var order = this.pos.get_order();
            const message = this.pos.config.picking_note_msg;

            // const inputPickingAddress = $('#picking-address');
            // if( !inputPickingAddress.val() ) {
            //     return alert( 'Keterangan Pengantaran harus diisi!' );
            // }
            // order.set_picking_address( inputPickingAddress.val() );
            order.set_picking_address( 'Alamat' );
            
            const orderlines = order.get_orderlines();
            const orderlineTable = $('#orderline-table');
            let index = 0;
            orderlines.forEach(orderline => {
                const tr = orderlineTable.children()[1].children[index];
                const checkbox = tr.children[0].children[0];
                const isChecked = checkbox.checked;
                const value = checkbox.value;
                const inputQty = tr.children[2].children[0];
                const qtyValue = inputQty.value;

                if( qtyValue > orderline.quantity ) {
                    return self.gui.show_popup('error', {
                        'title': _t('Error'),
                        'body': _t('Jumlah produk ' + orderline.product.display_name + ' yang dimasukkan melewati jumlah orderan (maksimal ' + orderline.quantity + ' )!'),
                    });
                }
                
                if( value == orderline.id && isChecked ) {
                    const qty_picking_str = qtyValue + ' ' + orderline.product.uom_id[1];
                    orderline.set_picking_note( message );
                    orderline.set_qty_picking( qtyValue, qty_picking_str );
                } else if ( value == orderline.id && !isChecked ) {
                    orderline.set_picking_note( '' );
                    orderline.set_qty_picking( 0, '' );
                }
                index++;
            });

            this.gui.close_popup();
        },
        renderElement: function() {
            var self = this;
            this._super();
            var order = this.pos.get_order();
            const orderlineTable = $('#orderline-table');
            const btnCancelPicking = $('#cancel-picking');
            const orderlines = order.get_orderlines();

            orderlines.forEach(orderline => {
                const input = document.createElement('input');
                input.type = 'checkbox';
                input.classList = 'orderline_id';
                input.value = orderline.id;
                input.style = 'min-height: 20px';
                input.checked = !(orderline.picking_note == '')
                
                const tdCheckbox = document.createElement('td');
                tdCheckbox.appendChild( input );

                const tdLine = document.createElement('td');
                tdLine.innerText = orderline.product.display_name;

                const inputQty = document.createElement('input');
                inputQty.type = 'number';
                inputQty.classList = 'orderline_id';
                inputQty.value = orderline.qty_picking ? orderline.qty_picking : orderline.quantity;
                inputQty.style = 'width: 60px';

                const tdQuantity = document.createElement('td');
                tdQuantity.appendChild( inputQty );

                const tr = document.createElement('tr');
                tr.appendChild( tdCheckbox );
                tr.appendChild( tdLine );
                tr.appendChild( tdQuantity );

                orderlineTable.append( tr );
            });

            btnCancelPicking.click(function() {
                orderlines.forEach(orderline => {
                    orderline.set_picking_note( '' );
                    orderline.set_qty_picking( 0 );
                });
                order.set_picking_address('');
                self.gui.close_popup();
            })

            // const inputPickingAddress = $('#picking-address');
            // inputPickingAddress.val( order.get_picking_address() );
        }
    });
    gui.define_popup({name:'pos_picking_note', widget: PosPickingNotePopup});

    var PickingNoteButton = screens.ActionButtonWidget.extend({
        template: "PosPickingNoteButton",
        button_click: function() {
			var order = this.pos.get_order();
            if(order.get_orderlines().length) {
                this.gui.show_popup('pos_picking_note');
            }
        }
    });
    screens.define_action_button({ name: 'picking_note', widget: PickingNoteButton});

    screens.ProductScreenWidget.include({
        handle_keypress: function(e) {
            this._super(e);

            var key = e.key;
            var mode = get_mode(e);
            if(mode === Mode.NORMAL) {
                if(key === 'a') {
                    document.querySelector('.pos-picking-note').click();
                }
            }
        }
    })

    function get_mode(e) {
        if (get_popup()) return Mode.POPUP
        else if ($(e.target).is('input')) return Mode.INSERT
        else return Mode.NORMAL

    }

    function get_popup() {
        return document.querySelector('.modal-dialog:not(.oe_hidden) .popup')
    }
});