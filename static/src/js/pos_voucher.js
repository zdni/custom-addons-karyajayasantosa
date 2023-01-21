odoo.define('ti_pos_retail.pos_voucher', function (require) {
    "use strict"

    var time = require('web.time');
    var gui = require('point_of_sale.gui');
	var models = require('point_of_sale.models');
	var screens = require('point_of_sale.screens');
	var PopupWidget = require('point_of_sale.popups');
	var Model = require('web.DataModel');
	var core = require('web.core');

	var _t = core._t;

	models.load_models('pos.config', ['enable_pos_voucher', 'voucher_journal_id'])

	var RedeemVoucherPopup = PopupWidget.extend({
		template: 'RedeemVoucherPopup',
		show: function(options) {
			var self = this;
			this.payment_self = options.payment_self;
			this._super(options);

			window.document.body.removeEventListener('keypress', this.payment_self.keyboard_handler);
			window.document.body.removeEventListener('keydown', this.payment_self.keyboard_keydown_handler);

			self.renderElement();
	    	$('.code_redeemed_voucher').focus();
		},
		click_confirm: function() {
			var self = this;
			var order = this.pos.get_order();
	    	const amount_redeemed_voucher = $('.amount_redeemed_voucher').text()*1;
	    	const code_redeemed_voucher = $('.code_redeemed_voucher').val();
	    	const name_redeemed_voucher = $('.name_redeemed_voucher').val();

			if( name_redeemed_voucher === '' && code_redeemed_voucher === '' && amount_redeemed_voucher === 0 ) return alert(_t("Check Voucher First"));

			if( !self.pos.config.voucher_journal_id ) return alert(_t("Please configure Journal for Voucher in Point of sale configuration."));
			if( amount_redeemed_voucher > order.get_total_without_tax() ) return alert(_t("Can not redeem more than order due."));

			var pos_voucher_cashregister = _.find(self.pos.cashregisters, function(cashregister){
				return cashregister.journal_id[0] === self.pos.config.voucher_journal_id[0] ? cashregister : false;
			});

			if( pos_voucher_cashregister ){
				order.add_paymentline( pos_voucher_cashregister );
				order.selected_paymentline.set_amount( amount_redeemed_voucher );
				order.selected_paymentline.set_amount_redeemed_voucher( amount_redeemed_voucher );
				order.selected_paymentline.set_code_redeemed_voucher( code_redeemed_voucher );
				order.selected_paymentline.set_name_redeemed_voucher( name_redeemed_voucher );
				order.selected_paymentline.set_freeze_line(true);
				self.payment_self.reset_input();
				self.payment_self.render_paymentlines();

				order.set_amount_redeemed_voucher( amount_redeemed_voucher );
				order.set_code_redeemed_voucher( code_redeemed_voucher );
				order.set_name_redeemed_voucher( name_redeemed_voucher );
				this.gui.close_popup();
			}
		},
		click_check: async function() {
			var order = this.pos.get_order();
			const curr_date = this.get_curr_date();

			const amount_redeemed_voucher = $('.amount_redeemed_voucher')
	    	const code_redeemed_voucher = $('.code_redeemed_voucher');
			const name_redeemed_voucher = $('.name_redeemed_voucher')
			let voucher = undefined;

			await new Model('pos.voucher')
				.query(['name', 'code', 'amount', 'minimum_purchase', 'expiry_date'])
				.filter([
					['code', '=', code_redeemed_voucher.val()],
					['expiry_date', '>=', curr_date],
				])
				.limit(1)
				.all()
				.then(function(vouchers){
					if( vouchers.length ) voucher = vouchers[0]
				})

			if (!voucher) return alert(_t("Kode Voucher tidak ditemukan"));
			if( order.get_total_without_tax() < voucher.minimum_purchase ) return alert(_t("Kode Voucher yang diklaim melebihi total belanja"));
		
			amount_redeemed_voucher.text( voucher.amount )
			name_redeemed_voucher.val( voucher.name )
		},
		renderElement: function() {
			var self = this;
			this._super();
			var order = this.pos.get_order();

			if( order ) {
				self.el.querySelector('.check-code-voucher').addEventListener('click', function(e) {
					self.click_check()
				})
			}

		},
		close: function() {
			window.document.body.addEventListener('keypress', this.payment_self.keyboard_handler);
			window.document.body.addEventListener('keydown', this.payment_self.keyboard_keydown_handler);
		},
		get_curr_date: function() {
			const date = new Date()
			return this.format_date( date )
		},
		format_date: function( date ) {
			const months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']

			const year = date.getFullYear()
			const month = months[date.getMonth()]
			const day = date.getDate() < 10 ? '0' + date.getDate() : date.getDate()

			return `${year}-${month}-${day}`
		}
	});
    gui.define_popup({name:'redeem_voucher', widget: RedeemVoucherPopup});

	var _super_order = models.Order.prototype;
	models.Order = models.Order.extend({
		initialize: function() {
			_super_order.initialize.apply(this, arguments);

			this.amount_redeemed_voucher = this.amount_redeemed_voucher || 0.00;
			this.code_redeemed_voucher = this.code_redeemed_voucher || '';
			this.name_redeemed_voucher = this.name_redeemed_voucher || '';
            this.save_to_db();
		},
		set_amount_redeemed_voucher: function(val) {
			this.amount_redeemed_voucher = Number(val).toFixed(2);
            this.trigger('change');
		},
		get_amount_redeemed_voucher: function() {
			return this.amount_redeemed_voucher;
		},
		set_code_redeemed_voucher: function(val) {
			this.code_redeemed_voucher = val;
            this.trigger('change');
		},
		get_code_redeemed_voucher: function() {
			return this.code_redeemed_voucher;
		},
		set_name_redeemed_voucher: function(val){
			this.name_redeemed_voucher = val;
			this.trigger('change');
    	},
    	get_name_redeemed_voucher: function(){
			return this.name_redeemed_voucher;
    	},
		remove_paymentline: function(line){
    		this.set_amount_redeemed_voucher(0);
    		this.set_code_redeemed_voucher('');
    		this.set_name_redeemed_voucher('');
    		_super_order.remove_paymentline.apply(this, arguments);
    	},
		export_as_JSON: function() {
            var json = _super_order.export_as_JSON.apply(this,arguments);
			json.amount_redeemed_voucher = this.amount_redeemed_voucher;
			json.code_redeemed_voucher = this.code_redeemed_voucher;
			json.name_redeemed_voucher = this.name_redeemed_voucher;
			return json;
		},
        init_from_JSON: function(json) {
            _super_order.init_from_JSON.apply(this,arguments);
            this.amount_redeemed_voucher = json.amount_redeemed_voucher;
            this.code_redeemed_voucher = json.code_redeemed_voucher;
            this.name_redeemed_voucher = json.name_redeemed_voucher;
        },
		export_for_printing: function() {
            var json = _super_order.export_for_printing.apply(this,arguments);
			json.amount_redeemed_voucher = this.get_amount_redeemed_voucher();
			json.code_redeemed_voucher = this.get_code_redeemed_voucher();
			json.name_redeemed_voucher = this.get_name_redeemed_voucher();
			return json;
		},
	});

	screens.PaymentScreenWidget.include({
		init: function(parent, options) {
			this._super(parent, options);
		},
		renderElement: function() {
			var self = this;
			this._super();

			var order = this.pos.get_order();

			this.$('.js_redeem_pos_vocher').click(function() {
				if( order ){
                    self.show_popup_redeem_voucher();
				}
			});
		},

		show_popup_redeem_voucher: function() {
			var order = this.pos.get_order();
			if( order ){
                this.gui.show_popup('redeem_voucher', {payment_self: this});
			}
		},
		payment_input: function(input) {
			var order = this.pos.get_order();
			this._super(input);
		}
	});

	var _super_paymentline = models.Paymentline.prototype;
	models.Paymentline = models.Paymentline.extend({
		initialize: function(attributes, options) {
			_super_paymentline.initialize.apply(this, arguments);
			this.set({
				amount_redeemed_voucher: 0.00,
				code_redeemed_voucher: 0.00,
				name_redeemed_voucher: 0.00,
			});
		},
		set_amount_redeemed_voucher: function(amount){
			this.set('amount_redeemed_voucher', amount);
		},
		get_amount_redeemed_voucher: function(){
			return this.get('amount_redeemed_voucher');
		},
		set_code_redeemed_voucher: function(points){
			this.set('code_redeemed_voucher', points);
		},
		get_code_redeemed_voucher: function(){
			return this.get('code_redeemed_voucher');
		},
		set_name_redeemed_voucher: function(points){
			this.set('name_redeemed_voucher', points);
		},
		get_name_redeemed_voucher: function(){
			return this.get('name_redeemed_voucher');
		},
		set_freeze_line: function(freeze_line){
        	this.set('freeze_line', freeze_line)
        },
        get_freeze_line: function(){
        	return this.get('freeze_line')
        },
	});

})