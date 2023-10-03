odoo.define('deposit_customer.pos', function (require) {
    "use strict"

    var gui = require('point_of_sale.gui');
	var models = require('point_of_sale.models');
	var screens = require('point_of_sale.screens');
	var PopupWidget = require('point_of_sale.popups');
	var Model = require('web.DataModel');
	var core = require('web.core');

	var _t = core._t;

	var RedeemDepositCustomerPopup = PopupWidget.extend({
		template: 'RedeemDepositCustomerPopup',
		show: function(options) {
			var self = this;
			this.payment_self = options.payment_self;
			this._super(options);

			var order = this.pos.get_order();
			var fields = _.find(this.pos.models,function(model){ return model.model === 'res.partner'; }).fields;
			
			if( order && order.get_client() ){
				new Model('res.partner').call('search_read', [[['id', '=', order.get_client().id]], fields], {}, {async: false})
					.then(function(partner) {
						if(partner.length > 0){
							var exist_partner = self.pos.db.get_partner_by_id(order.get_client().id);
							_.extend(exist_partner, partner[0]);
						}
					});
			}
			
			window.document.body.removeEventListener('keypress', this.payment_self.keyboard_handler);
			window.document.body.removeEventListener('keydown', this.payment_self.keyboard_keydown_handler);

			self.renderElement();
	    	$('.redeem_deposit').focus();
		},
		click_confirm: function() {
			var self = this;
			var order = this.pos.get_order();
	    	var redeem_deposit = $('.redeem_deposit');

			if( redeem_deposit.val() && $.isNumeric(redeem_deposit.val()) && Number(redeem_deposit.val()) > 0 ) {
				var deposit_customer = order.get_client().total_deposit; 
				if( Number(redeem_deposit.val()) <= deposit_customer ) {
					if( redeem_deposit.val() <= (order.get_due() ) ){
						if( self.pos.config.deposit_journal_id ){
							var deposit_cashregister = _.find(self.pos.cashregisters, function(cashregister){
								return cashregister.journal_id[0] === self.pos.config.deposit_journal_id[0] ? cashregister : false;
							});

							if( deposit_cashregister ){
								order.add_paymentline( deposit_cashregister );
								order.selected_paymentline.set_amount( redeem_deposit.val() );
								order.selected_paymentline.set_deposit_redeemed( redeem_deposit.val() );
								order.selected_paymentline.set_freeze_line(true);
								self.payment_self.reset_input();
								self.payment_self.render_paymentlines();
								order.set_deposit_redeemed_amount(Number(redeem_deposit.val()));

								this.gui.close_popup();
							}
						} else {
							alert(_t("Please configure Journal for Deposit in Point of sale configuration."));
						}
					} else {
	    				alert(_t("Can not redeem more than order due."));
	    			}
				} else {
	    			alert(_t("Input must be <= "+ deposit_customer));
				}
			} else {
	    		alert(_t("Invalid Input"));
			}
		},
		renderElement: function() {
			var self = this;
			this._super();
			var order = this.pos.get_order();

			if(self.el.querySelector('.redeem_deposit')){
		    	self.el.querySelector('.redeem_deposit').addEventListener('keyup', function(e){
					if($.isNumeric($(this).val())){
		    			var deposit_customer = order.get_client().total_point;
		    			var amount = Number($(this).val() );

		    			if(Number($(this).val()) > deposit_customer){
		    				alert("Can not redeem more than deposit customer");
		    				$(this).val(0);
		    			}
		    			if(amount > order.get_due()){
		    				alert("Deposit exceeding Due Amount");
		    				$(this).val(0);
		    			}
		    		}
		    	});
	    	}
		},
		close: function() {
			window.document.body.addEventListener('keypress', this.payment_self.keyboard_handler);
			window.document.body.addEventListener('keydown', this.payment_self.keyboard_keydown_handler);
		},
	});
    gui.define_popup({name:'redeem_deposit_customer', widget: RedeemDepositCustomerPopup});

	var _super_order = models.Order.prototype;
	models.Order = models.Order.extend({
		initialize: function(attributes, options) {
			_super_order.initialize.apply(this, arguments);
			this.set({ 
				deposit_income_amount: 0.00,
				deposit_redeemed_amount: 0.00,
			})
		},
		get_deposit_customer_format: function() {
			let deposit = this.get_client() ? this.get_client().total_deposit.toFixed(2) : 0.00;
			var str = "" + deposit
			str = new Intl.NumberFormat("id-ID", {style: "currency", currency: "IDR"}).format(str);
			str = str.replace(/[Rp\s]/g, '')
    		return str;
		},
		set_deposit_income_amount: function(val){
    		this.set('deposit_income_amount', val);
    	},
    	get_deposit_income_amount: function(){
    		return this.get('deposit_income_amount') || 0.00;
    	},
		set_deposit_redeemed_amount: function(val){
    		this.set('deposit_redeemed_amount', val);
    	},
    	get_deposit_redeemed_amount: function(){
    		return this.get('deposit_redeemed_amount') || 0.00;
    	},
		get_deposit_redeemed_amount_format: function() {
			let redeem = this.get('deposit_redeemed_amount') || 0.00;
			var str = "" + redeem
			str = new Intl.NumberFormat("id-ID", {style: "currency", currency: "IDR"}).format(str);
			str = str.replace(/[Rp\s]/g, '')
    		return str;
		},
		get_total_deposit: function(){
    		var temp = 0
    		if(this.get_client()){
	    		temp = Number(this.get_client().total_deposit) 
						+ Number(this.get_deposit_income_amount())
	    				- Number(this.get_deposit_redeemed_amount())
    		}
    		return temp.toFixed()
    	},
		get_total_deposit_format: function() {
    		var temp = 0
    		if(this.get_client()){
	    		temp = Number(this.get_client().total_deposit) 
						+ Number(this.get_deposit_income_amount())
	    				- Number(this.get_deposit_redeemed_amount())
    		}
			temp = temp.toFixed()
			var str = "" + temp
			str = new Intl.NumberFormat("id-ID", {style: "currency", currency: "IDR"}).format(str);
			str = str.replace(/[Rp\s]/g, '')
    		return str;
		},
		remove_paymentline: function(line){
			if(line.cashregister.journal_id[0] === this.pos.config.deposit_journal_id[0]) {
				this.set_deposit_redeemed_amount(0);
			}
    		_super_order.remove_paymentline.apply(this, arguments);
    	},
		export_as_JSON: function() {
			var order = _super_order.export_as_JSON.call(this);
			var new_val = {
    			deposit_customer: this.get_client() ? this.get_client().total_deposit.toFixed(2) : false,
            	deposit_income: this.get_deposit_income_amount() || false,
            	deposit_redeemed: this.get_deposit_redeemed_amount() || false,
            	total_deposit: this.get_total_deposit() || false,
			}
			$.extend(order, new_val);

			return order;
		},
		export_for_printing: function() {
			var receipt = _super_order.export_for_printing.call(this);

			var new_val = {
    			deposit_customer: this.get_client() ? this.get_client().total_deposit.toFixed(2) : false,
    			deposit_customer_format: this.get_deposit_customer_format(),
    			deposit_income: this.get_deposit_income_amount() || false,
    			deposit_redeemed: this.get_deposit_redeemed_amount() || false,
    			deposit_redeemed_format: this.get_deposit_redeemed_amount_format() || false,
				total_deposit: this.get_total_deposit() || false,
				total_deposit_format: this.get_total_deposit_format() || false,
			}
			$.extend(receipt, new_val);

			receipt.is_member = this.is_member;
			return receipt;
		},
	});

	screens.ActionpadWidget.include({
		renderElement: function() {
            const self = this;
            this._super();

            this.$('.pay').click(function(){
                const order = self.pos.get_order();
                const orderlines = order.get_orderlines();
                let deposit = 0;
				let have_deposit = false;

                for (let index = 0; index < orderlines.length; index++) {
                    const orderline = orderlines[index];
                    const product = orderline.product;
                    
					if( self.pos.config.deposit_product_id[0] === product.id ){
						deposit += orderline.price
						have_deposit = true;
					}
                }

				if( !order.get_client() && deposit > 0 && have_deposit ) {
					self.gui.back();
                    return self.pos.gui.show_popup('error', {
						title: '!!! Warning !!!',
                        body: 'Silahkan Pilih Customer untuk deposit ini !!!'
                    });
				}
				if( deposit < 0 && have_deposit && (Number(order.get_client().total_deposit) < deposit*-1) ) {
					self.gui.back();
                    return self.pos.gui.show_popup('error', {
						title: '!!! Warning !!!',
                        body: 'Pengeluaran Deposit lebih besar dari Deposit yang dimiliki Customer !!!'
                    });
				}
				order.set_deposit_income_amount(deposit)
            });
        },
	})

	screens.PaymentScreenWidget.include({
		init: function(parent, options) {
			this._super(parent, options);
		},
		renderElement: function() {
			var self = this;
			this._super();

			var order = this.pos.get_order();

			this.$('.js_redeem_deposit_customer').click(function() {
				if( order ){
					if( order.get_client() ){
                        if( order.get_client().total_deposit > 0 ){
                            self.show_popup_deposit_customer();
                        } else {
                            self.gui.show_popup('error', {
                                title: _t("Deposit Customer"),
                                body: _t(order.get_client().name + " tidak memiliki deposit customer"),
                            });
                        }
					} else {
						self.gui.show_popup('error', {
							title: _t("Deposit Customer"),
							body: _t("Silahkan pilih customer terlebih dahulu!"),
						});
					}
				}
			});
		},
		show_popup_deposit_customer: function() {
			var order = this.pos.get_order();
			if( order ){
				if( order.get_client() ) {
					this.gui.show_popup('redeem_deposit_customer', {payment_self: this});
				}
			}
		},
		payment_input: function(input) {
			// var order = this.pos.get_order();
			// if( order.selected_paymentline.get_freeze_line() ) {
			// 	return;
			// }
			this._super(input);
		}
	});

	var _super_paymentline = models.Paymentline.prototype;
	models.Paymentline = models.Paymentline.extend({
		initialize: function(attributes, options) {
			_super_paymentline.initialize.apply(this, arguments);
			this.set({ deposit_redeemed: 0.00 });
		},
		set_deposit_redeemed: function(points){
			this.set('deposit_redeemed', points);
		},
		get_deposit_redeemed: function(){
			return this.get('deposit_redeemed');
		},
		set_freeze_line: function(freeze_line){
        	this.set('freeze_line', freeze_line)
        },
        get_freeze_line: function(){
        	return this.get('freeze_line')
        },
	});

});