odoo.define('pos_bank_charge.pos_bank_charge', function (require) {
    "use strict"

    var gui = require('point_of_sale.gui');
	var models = require('point_of_sale.models');
	var screens = require('point_of_sale.screens');
	var PopupWidget = require('point_of_sale.popups');
	var core = require('web.core');

	var _t = core._t;

	models.load_fields('pos.order', ['tatal_bank_charge', 'has_bank_charge']);
    var Mode = Object.freeze({ INSERT: 1, NORMAL: 2, POPUP: 3 })

	var _super_order = models.Order.prototype;
	models.Order = models.Order.extend({
		initialize: function() {
			_super_order.initialize.apply(this, arguments);
            this.has_bank_charge = this.has_bank_charge || false;
            this.total_bank_charge = this.total_bank_charge || 0.00;
		},
		export_as_JSON: function() {
			var json = _super_order.export_as_JSON.apply(this, arguments);
			json.has_bank_charge = this.has_bank_charge;
			json.total_bank_charge = this.total_bank_charge;
			return json;
		},
        init_from_JSON: function(json){
            _super_order.init_from_JSON.apply(this,arguments);
            this.has_bank_charge = json.has_bank_charge;
            this.total_bank_charge = json.total_bank_charge;
        },
        export_for_printing: function () {
            var json = _super_order.export_for_printing.apply(this, arguments);
            json.has_bank_charge = this.get_has_bank_charge();
            json.total_bank_charge = this.get_total_bank_charge();
            return json;
        },
		set_has_bank_charge: function(val) {
			this.has_bank_charge = val;
		},
		get_has_bank_charge: function() {
			return this.has_bank_charge;
		},
		set_total_bank_charge: function(total_bank_charge) {
			this.total_bank_charge = total_bank_charge;
		},
		get_total_bank_charge: function() {
			return this.total_bank_charge;
		},
		get_total_with_tax: function() {
			var total_with_tax = _super_order.get_total_with_tax.call(this);
			return total_with_tax + this.get_total_bank_charge();
		},
	});

	var PosBankChargePopup = PopupWidget.extend({
		template: 'PosBankChargePopup',
		show: function(options) {
			var self = this;
			this.payment_self = options.payment_self;
			this._super(options);

			var order = this.pos.get_order();
			window.document.body.removeEventListener('keypress', this.payment_self.keyboard_handler);
			window.document.body.removeEventListener('keydown', this.payment_self.keyboard_keydown_handler);

			self.renderElement();
	    	$('.bank_charge_input').focus();
		},
		click_confirm: function() {
			const self = this;
			const order = this.pos.get_order();
			const enable_pos_bank_charge = this.pos.config.enable_pos_bank_charge;
	    	const bank_charge_input = $('.bank_charge_input');
			const type_charge = $('select[name=type_charge] option').filter(':selected').val();
			const bank_payment = $('select[name=bank_payment] option').filter(':selected').val();
			
			const span_total_bank_charge = $('.total_bank_charge');
			const input_total_bank_charge = $('.input_total_bank_charge');
			
			const btn_pos_bank_charge = $('.js_pos_bank_charge');
			const btn_remove_pos_bank_charge = $('.js_remove_pos_bank_charge');

			if( !enable_pos_bank_charge ) {
				return self.gui.show_popup('error', {
					title: _t("POS Bank Charge"),
					body: _t("Silahkan aktifkan fitur ini terlebih dahulu!"),
				});
			}
			
			if( bank_charge_input.val() && $.isNumeric( bank_charge_input.val() ) && Number( bank_charge_input.val() ) >= 0 ) {
				const total_bank_charge = self.count_bank_charge( bank_charge_input.val(), type_charge ); 

				span_total_bank_charge.text( total_bank_charge );
				input_total_bank_charge.val( total_bank_charge );

				if( !bank_payment ) {
					return self.gui.show_popup('error', {
						title: _t("POS Bank Charge"),
						body: _t("Silahkan pilih bank untuk pembayaran!"),
					});
				}

				const cashregister = _.find(self.pos.cashregisters, function(cash){
					return cash.journal_id[0] === +bank_payment ? cash : false;
				});

				if( !cashregister ) {
					return self.gui.show_popup('error', {
						title: _t("POS Bank Charge"),
						body: _t("Bank yang anda pilih tidak terdaftar dalam metode pembayaran!"),
					});
				}

				// tambah bank charge
				order.set_has_bank_charge( true );
				order.set_total_bank_charge( total_bank_charge );
				
				btn_remove_pos_bank_charge.removeClass('hidden');
				btn_pos_bank_charge.addClass('hidden');

				order.add_paymentline( cashregister );
				order.selected_paymentline.set_amount( order.get_total_with_tax() );
				self.payment_self.reset_input();
				self.payment_self.render_paymentlines();

				this.gui.close_popup();
			} else {
				return self.gui.show_popup('error', {
					title: _t("POS Bank Charge"),
					body: _t("Invalid Input!"),
				});
			}
		},
		renderElement: function() {
			var self = this;
			this._super();
			const span_total_bank_charge = $('.total_bank_charge');
			const input_total_bank_charge = $('.input_total_bank_charge');

			if(self.el.querySelector('.bank_charge_input')){
		    	self.el.querySelector('.bank_charge_input').addEventListener('keyup', function(e){
					var bank_charge_input_val = $(this).val();
					
					if($.isNumeric( bank_charge_input_val )){
						var type_charge = $('select[name=type_charge] option').filter(':selected').val();
						const total_bank_charge = self.count_bank_charge( bank_charge_input_val, type_charge );	
						if( total_bank_charge ) {
							span_total_bank_charge.text( total_bank_charge );
							input_total_bank_charge.val( total_bank_charge );
						}
		    		} else {
						span_total_bank_charge.text( '0.00' );
						input_total_bank_charge.val( 0.00 );
		    		}
		    	});
	    	}
			this.render_combo_box_payment();
		},
		render_combo_box_payment: function() {
			const self = this;
			const bank_payment = $('.bank_payment');

			const cashregisters = self.pos.cashregisters;
			cashregisters.forEach(cashregister => {
				if( cashregister.journal.type == 'bank' ) {
					const option = new Option("value", cashregister.journal_id[0]);
					$(option).html(cashregister.journal_id[1]);
					bank_payment.append(option);
				}
			});
		},
		count_bank_charge: function( bank_charge, type_charge ) {
			const self = this;
			const order = self.pos.get_order();
			const amount_due = order.get_due() || order.get_total_with_tax();
			let total_bank_charge = 0;

			if( type_charge !== 'Fix' && type_charge !== 'Persentase' ) {
				self.gui.show_popup('error', {
					title: _t("POS Bank Charge"),
					body: _t("Silahkan pilih tipe charge!"),
				});
				return false;
			}

			if( type_charge == 'Fix' ) {
				total_bank_charge = bank_charge; 
			} else if( type_charge == 'Persentase' ) {
				total_bank_charge = amount_due*bank_charge/100;
			}
			return total_bank_charge;

		},
		close: function() {
			window.document.body.addEventListener('keypress', this.payment_self.keyboard_handler);
			window.document.body.addEventListener('keydown', this.payment_self.keyboard_keydown_handler);
		},
	});
    gui.define_popup({name:'pos_bank_charge', widget: PosBankChargePopup});

	screens.PaymentScreenWidget.include({
		init: function(parent, options) {
			this._super(parent, options);
		},

		renderElement: function() {
			var self = this;
			this._super();

			var order = this.pos.get_order();
			const btn_pos_bank_charge = this.$('.js_pos_bank_charge');
			const btn_remove_pos_bank_charge = this.$('.js_remove_pos_bank_charge');

			btn_pos_bank_charge.click(function() {
				if( order ){
					if( self.pos.config.enable_pos_bank_charge && self.pos.config.bank_charge_product_id[0] ){
						self.show_popup_pos_bank_charge();
					} else {
						self.gui.show_popup('error', {
							title: _t("POS Bank Charge"),
							body: _t("Silahkan aktifkan fitur terlebih dahulu!"),
						});
					}

				}
			});
			btn_remove_pos_bank_charge.click(function() {
				if( order ){
					order.set_has_bank_charge( false );
					order.set_total_bank_charge( 0 );

					const lines = order.get_paymentlines();
					for (let index = 0; index < lines.length; index++) {
						const line = lines[index];
						order.remove_paymentline( line );
						self.reset_input();
						self.render_paymentlines();
					}

					btn_remove_pos_bank_charge.addClass('hidden');
					btn_pos_bank_charge.removeClass('hidden');
				}
			});

			if( order.get_has_bank_charge() ) {
				btn_remove_pos_bank_charge.removeClass('hidden');
				btn_pos_bank_charge.addClass('hidden');
			}
		},
		show_popup_pos_bank_charge: function() {
			var order = this.pos.get_order();
			if( order ){
				if( this.pos.config.enable_pos_bank_charge && this.pos.config.bank_charge_product_id[0] ) {
					this.gui.show_popup('pos_bank_charge', {payment_self: this});
				}
			}
		},
		finalize_validation: function() {
			const self = this;
			const order = self.pos.get_order();
			
			const bank_charge_product_id = self.pos.config.bank_charge_product_id;
			const product = self.pos.db.get_product_by_id( bank_charge_product_id[0] );

			// tambah produk bank charge
			if( order.has_bank_charge ) {
				order.add_product(product, {
					price: order.get_total_bank_charge(),
					extras: {
						price_manually_set: true,
					},
				});
				order.set_total_bank_charge( 0 );
			}

			this._super();
		},
		handle_keyup: function(e) {
			const order = this.pos.get_order();
            this._super(e);

			var key = e.key;
            var mode = get_mode(e);
            if(mode === Mode.NORMAL) {
                if(key === 'q' && !order.has_bank_charge) {
                    document.querySelector('.js_pos_bank_charge').click();
                }
				if(key === 'w' && order.has_bank_charge) {
                    document.querySelector('.js_remove_pos_bank_charge').click();
                }
            }
		}
	});

    function get_mode(e) {
        if (get_popup()) return Mode.POPUP
        else if ($(e.target).is('input')) return Mode.INSERT
        else return Mode.NORMAL

    }

    function get_popup() {
        return document.querySelector('.modal-dialog:not(.oe_hidden) .popup')
    }
});