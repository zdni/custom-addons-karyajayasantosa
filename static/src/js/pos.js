odoo.define('loyalty_point.pos', function (require) {
    "use strict"

    var gui = require('point_of_sale.gui');
	var models = require('point_of_sale.models');
	var screens = require('point_of_sale.screens');
	var PopupWidget = require('point_of_sale.popups');
	var Model = require('web.DataModel');
	var core = require('web.core');
	var DB = require('point_of_sale.DB');
	var utils = require('web.utils');

	var QWeb = core.qweb;
	var _t = core._t;
	var round_di = utils.round_decimals;
	var round_pr = utils.round_precision;

    models.load_fields('res.partner', [
		'card_number_lyt', 'member_status', 'member_loyalty_level_id', 'total_points', 'total_remaining_points', 'config_member'
	]);
	models.load_fields('product.product', ['not_earn_loyatly_point']);

    var _super_posmodel = models.PosModel;
	models.PosModel = models.PosModel.extend({
		load_server_data: function() {
			var self = this;
			var loaded = _super_posmodel.prototype.load_server_data.call(this);
			loaded.then(function() {
				// load model loyalty level configuration
				var limit = 3, sort = 'id desc', domain = [], fields = [], offset;
				new Model('loyalty.level.configuration').call('search_read', 
		    			[domain=domain, fields=fields, offset=0, limit=limit, sort=sort], {}, {async: false})
				.then(function( loyalty_level_configurations ){
					self.loyalty_level_configuration = {};
					if( loyalty_level_configurations ){
						for(var index = 0; index < loyalty_level_configurations.length; index++){
							const loyalty_level_configuration = loyalty_level_configurations[index];
							self.loyalty_level_configuration[ loyalty_level_configuration.id ] = loyalty_level_configuration;
						}
					}
				});
			});
			return loaded;
		},
	});

	DB.include({
		add_partners: function(partners) {
			var self = this;
			for( var i = 0; i < partners.length; i++ ) {
				var partner = partners[i];
				var old_partner = this.partner_by_id[partner.id];
				if(partners && old_partner && partner.total_remaining_points !== old_partner.total_remaining_points){
	            	old_partner['total_remaining_points'] = partner.total_remaining_points;
	            }
			}
			return this._super(partners);
		}
	});

	var RedeemLoyaltyPointsPopup = PopupWidget.extend({
		template: 'RedeemLoyaltyPointsPopup',
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
	    	$('.redeem_loyalty_input').focus();
		},
		click_confirm: function() {
			var self = this;
			var order = this.pos.get_order();
	    	var redeem_point_input = $('.redeem_loyalty_input');

			const member_loyalty_level_id = ( order.attributes.client !== null ) ? order.attributes.client.member_loyalty_level_id[0] : false;
			const loyalty_config = this.pos.loyalty_level_configuration[member_loyalty_level_id];

			if( redeem_point_input.val() && $.isNumeric(redeem_point_input.val()) && Number(redeem_point_input.val()) > 0 ) {
				var total_remaining_points = order.get_client().total_remaining_points - order.get_loyalty_redeemed_point(); 
				if( Number(redeem_point_input.val()) <= total_remaining_points ) {
					var amount_to_redeem = (Number(redeem_point_input.val()) * loyalty_config.to_amount) / loyalty_config.points;
					if( amount_to_redeem <= (order.get_due() || order._calculate_total_order_without_product_not_earned() ) ){
						if( self.pos.config.loyalty_journal_id ){
							var loyalty_cashregister = _.find(self.pos.cashregisters, function(cashregister){
								return cashregister.journal_id[0] === self.pos.config.loyalty_journal_id[0] ? cashregister : false;
							});

							if( loyalty_cashregister ){
								order.add_paymentline( loyalty_cashregister );
								order.selected_paymentline.set_amount( amount_to_redeem );
								order.selected_paymentline.set_loyalty_point( redeem_point_input.val() );
								order.selected_paymentline.set_freeze_line(true);
								self.payment_self.reset_input();
								self.payment_self.render_paymentlines();
								order.set_loyalty_redeemed_point(Number(order.get_loyalty_redeemed_point()) + Number(redeem_point_input.val()));
								order.set_loyalty_redeemed_amount(order.get_loyalty_amount_by_point(order.get_loyalty_redeemed_point()));

								order.set_loyalty_earned_point( 
									order._calculate_earned_point( 
										order._calculate_total_order_without_product_not_earned(), 
										order.get_loyalty_redeemed_point() || 0.00 
									)
								);
								this.gui.close_popup();
							}
						} else {
							alert(_t("Please configure Journal for Loyalty in Point of sale configuration."));
						}
					} else {
	    				alert(_t("Can not redeem more than order due."));
	    			}
				} else {
	    			alert(_t("Input must be <= "+ total_remaining_points));
				}
			} else {
	    		alert(_t("Invalid Input"));
			}
		},
		renderElement: function() {
			var self = this;
			this._super();
			var order = this.pos.get_order();

			if(self.el.querySelector('.redeem_loyalty_input')){
		    	self.el.querySelector('.redeem_loyalty_input').addEventListener('keyup', function(e){
					if($.isNumeric($(this).val())){
		    			var total_remaining_points = order.get_client().total_remaining_points - order.get_loyalty_redeemed_point();
		    			var amount = order.get_loyalty_amount_by_point( Number($(this).val() ));

		    			$('.point_to_amount').text(self.format_currency(amount));
		    			if(Number($(this).val()) > total_remaining_points){
		    				alert("Can not redeem more than your remaining points");
		    				$(this).val(0);
		    				$('.point_to_amount').text('0.00');
		    			}
		    			if(amount > (order.get_due() || order._calculate_total_order_without_product_not_earned())){
		    				alert("Loyalty Amount exceeding Due Amount");
		    				$(this).val(0);
		    				$('.point_to_amount').text('0.00');
		    			}
		    		} else {
		    			$('.point_to_amount').text('0.00');
		    		}
		    	});
	    	}
			this.render_table_loyalty_points();
		},
		close: function() {
			window.document.body.addEventListener('keypress', this.payment_self.keyboard_handler);
			window.document.body.addEventListener('keydown', this.payment_self.keyboard_keydown_handler);
		},
		render_table_loyalty_points: function() {
			var self = this;
			var order = this.pos.get_order();
			var client = this.pos.get_order().get_client()
			var table_loyalty_points = '<tr><th>Point</th><th>Tanggal Kadaluarsa</th></tr>';

			if(client){
				var partner_id = client.id;
				if(partner_id){
					new Model('earned.point.record')
						.query(['points', 'expired_date'])
						.filter([
							['partner_id', '=', partner_id],
							['state', '=', 'open']
						])
						.limit(3)
						.all()
						.then(function(records){
							records.map((record) => {
								table_loyalty_points += '<tr>'
								table_loyalty_points += '<td>'+record.points+'</td>'
								table_loyalty_points += '<td>'+record.expired_date+'</td>'
								table_loyalty_points += '</tr>';
							})
						})
						$('#table_loyalty_points tbody').html(table_loyalty_points);
				}
			}
		}
	});
    gui.define_popup({name:'redeem_loyalty_points', widget: RedeemLoyaltyPointsPopup});

	var _super_order = models.Order.prototype;
	models.Order = models.Order.extend({
		initialize: function(attributes, options) {
			_super_order.initialize.apply(this, arguments);
			this.is_member = this.is_member || false;
			this.set({
				loyalty_earned_point: 0.00,
				loyalty_redeemed_point: 0.00,
			})
		},
		set_loyalty_earned_point: function(val) {
			this.set('loyalty_earned_point', val);
		},
		get_loyalty_earned_point: function() {
			return this.get('loyalty_earned_point') || 0.00;
		},
		set_loyalty_earned_amount: function(val){
    		this.set('loyalty_earned_amount', val);
    	},
    	get_loyalty_earned_amount: function(){
    		return this.get('loyalty_earned_amount') || 0.00;
    	},
		set_loyalty_redeemed_point: function(val) {
			this.set('loyalty_redeemed_point', Number(val).toFixed(2));
		},
		get_loyalty_redeemed_point: function() {
			return this.get('loyalty_redeemed_point') || 0.00;
		},
		set_loyalty_redeemed_amount: function(val){
    		this.set('loyalty_redeemed_amount', val);
    	},
    	get_loyalty_redeemed_amount: function(){
    		return this.get('loyalty_redeemed_amount') || 0.00;
    	},
		get_loyalty_redeemed_point_format: function() {
			let redeem = this.get('loyalty_redeemed_point') || 0.00;
			var str = "" + redeem
			str = new Intl.NumberFormat("id-ID", {style: "currency", currency: "IDR"}).format(str);
			str = str.replace(/[Rp\s]/g, '')
    		return str;
		},
		get_loyalty_earned_point_format: function() {
			let earned = this.get('loyalty_earned_point') || 0.00;
			var str = "" + earned
			str = new Intl.NumberFormat("id-ID", {style: "currency", currency: "IDR"}).format(str);
			str = str.replace(/[Rp\s]/g, '')
    		return str;
		},
		get_yout_points_format: function() {
			let points = this.get_client() ? this.get_client().total_remaining_points.toFixed(2) : 0.00;
			var str = "" + points
			str = new Intl.NumberFormat("id-ID", {style: "currency", currency: "IDR"}).format(str);
			str = str.replace(/[Rp\s]/g, '')
    		return str;
		},
		export_as_JSON: function() {
			var order = _super_order.export_as_JSON.call(this);
			var new_earned_point = this._calculate_earned_point( this._calculate_total_order_without_product_not_earned(), this.get_loyalty_redeemed_point() || 0.00 );
			var new_earned_amount = this.get_loyalty_amount_by_point(new_earned_point);

			var new_val = {
            	loyalty_earned_amount: new_earned_amount || false,
				loyalty_earned_point: new_earned_point || false,
            	loyalty_redeemed_amount: this.get_loyalty_redeemed_amount() || false,
				loyalty_redeemed_point: this.get_loyalty_redeemed_point() || false,	
			}
			$.extend(order, new_val);

			order.is_member = this.is_member;
			return order;
		},
		remove_paymentline: function(line){
    		this.set_loyalty_redeemed_point(this.get_loyalty_redeemed_point() - line.get_loyalty_point());
    		this.set_loyalty_redeemed_amount(this.get_loyalty_amount_by_point(this.get_loyalty_redeemed_point()));
    		_super_order.remove_paymentline.apply(this, arguments);
    	},
		get_total_loyalty_points: function(){
			var new_earned_point = this._calculate_earned_point( this._calculate_total_order_without_product_not_earned(), this.get_loyalty_redeemed_point() || 0.00 );

    		var temp = 0
    		if(this.get_client()){
	    		temp = Number(this.get_client().total_remaining_points) 
	    				+ Number( new_earned_point ) 
	    				- Number(this.get_loyalty_redeemed_point())
    		}
    		return temp.toFixed()
    	},
		get_total_loyalty_points_format: function() {
			var new_earned_point = this._calculate_earned_point( this._calculate_total_order_without_product_not_earned(), this.get_loyalty_redeemed_point() || 0.00 );

    		var temp = 0
    		if(this.get_client()){
	    		temp = Number(this.get_client().total_remaining_points) 
	    				+ Number( new_earned_point ) 
	    				- Number(this.get_loyalty_redeemed_point())
    		}
			temp = temp.toFixed()
			var str = "" + temp
			str = new Intl.NumberFormat("id-ID", {style: "currency", currency: "IDR"}).format(str);
			str = str.replace(/[Rp\s]/g, '')
    		return str;
		},
		get_new_earned_point_format: function() {
			var new_earned_point = this._calculate_earned_point( this._calculate_total_order_without_product_not_earned(), this.get_loyalty_redeemed_point() || 0.00 );
			var str = "" + new_earned_point
			str = new Intl.NumberFormat("id-ID", {style: "currency", currency: "IDR"}).format(str);
			str = str.replace(/[Rp\s]/g, '')
    		return str;
		},
		export_for_printing: function() {
			var receipt = _super_order.export_for_printing.call(this);
			var new_earned_point = this._calculate_earned_point( this._calculate_total_order_without_product_not_earned(), this.get_loyalty_redeemed_point() || 0.00 );

			var new_val = {
				total_points: this.get_total_loyalty_points() || false,
				total_points_format: this.get_total_loyalty_points_format() || false,
    			earned_points: new_earned_point || false,
    			earned_points_format: this.get_new_earned_point_format() || false,
    			redeem_points: this.get_loyalty_redeemed_point() || false,
    			redeem_points_format: this.get_loyalty_redeemed_point_format() || false,
    			client_points: this.get_client() ? this.get_client().total_remaining_points.toFixed(2) : false,
    			client_points_format: this.get_yout_points_format(),
			}
			$.extend(receipt, new_val);

			receipt.is_member = this.is_member;
			return receipt;
		},
		get_loyalty_amount_by_point: function(point) {
			var order = this.pos.get_order();
			if( order  ){
				var member_loyalty_level_id = (order.get_client()) ? order.get_client().member_loyalty_level_id[0] : false;
				var loyalty_config = (member_loyalty_level_id) ? this.pos.loyalty_level_configuration[ member_loyalty_level_id ] : false;

				if (loyalty_config) {
					return (point * loyalty_config.to_amount ) / loyalty_config.points;
				}
			}
			return 0;
		},

		_calculate_total_order_without_product_not_earned: function() {
			let total = 0;
			const order = this.pos.get_order();
			if( !order ) return total;
			
			const orderlines = order.orderlines.models;
			if( !orderlines.length ) return total;

			for (let index = 0; index < orderlines.length; index++) {
				const orderline = orderlines[index];
				const product = orderline.product;
				
				if( !product.not_earn_loyatly_point ) {
					total += (orderline.price * orderline.quantity) - orderline.discount;
				}
			}
			return total;
		},
		_calculate_earned_point: function(total, redeem) {
			if( this.attributes ){
				const partner_id = ( this.attributes.client !== null ) ? this.attributes.client.id : false;
				const member_loyalty_level_id = ( this.attributes.client !== null ) ? this.attributes.client.member_loyalty_level_id[0] : false;

				if( partner_id && member_loyalty_level_id ) {
					const loyalty_config = this.pos.loyalty_level_configuration[member_loyalty_level_id];
					let earned_points = 0;
					if (loyalty_config.type == 'percentage'){
						earned_points = ( (total - redeem) * loyalty_config.point_calculation_percentage ) / 100;
					} else if (loyalty_config.type == 'fix'){
						earned_points = loyalty_config.point_calculation_fix;
					} else if (loyalty_config.type == 'fix_multiple'){
						earned_points = parseInt(( (total - redeem) / loyalty_config.amount_multiple )) * loyalty_config.point_calculation_fix_multiple;
					}

					return (total - redeem) >= loyalty_config.minimum_purchase ? earned_points : 0;
				}
			}
			return 0;
		},
	});

	screens.OrderWidget.include({
		update_summary: function() {
			this._super();
			var order = this.pos.get_order();

			if( !order.get_orderlines().length ) {
				return;
			}
			this.hidden_loyalty_info_cart();
			if( order.get_client() ) {
				var total_points = order._calculate_earned_point( order._calculate_total_order_without_product_not_earned(), order.get_loyalty_redeemed_point() || 0.00 );
				
				!total_points ? this.hidden_loyalty_info_cart() : this.show_loyalty_info_cart();

				if( this.el.querySelector('.loyalty_info_cart .value') ) {
					this.el.querySelector('.loyalty_info_cart .value').textContent = total_points;

					order.set_loyalty_earned_point( total_points );
		        	order.set_loyalty_earned_amount( order.get_loyalty_amount_by_point(total_points) );
				}
			}
		},
		hidden_loyalty_info_cart: function() {
			if( document.getElementsByClassName('loyalty_info_cart')[0] ){
				document.getElementsByClassName('loyalty_info_cart')[0].classList.add('oe_hidden');
			}
		},
		show_loyalty_info_cart: function() {
			if( document.getElementsByClassName('loyalty_info_cart')[0] ){
				document.getElementsByClassName('loyalty_info_cart')[0].classList.remove('oe_hidden');
			}
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

			this.$('.js_redeem_loyalty_point').click(function() {
				if( order ){
					if( order.get_client() ){
						if( order.get_client().config_member == 'loyalty' ){
							if( order.get_client().member_status ) {
								if( order.get_client().total_remaining_points > 0 ){
									self.show_popup_redeem_loyalty();
								} else {
									self.gui.show_popup('error', {
										title: _t("Loyalty Points"),
										body: _t(order.get_client().name + " memiliki 0 point untuk melakukan redeem"),
									});
								}
							}
						} else {
							self.gui.show_popup('error', {
								title: _t("Member Status"),
								body: _t(order.get_client().name + " menggunakan member cashback"),
							});
						}
					} else {
						self.gui.show_popup('error', {
							title: _t("Loyalty Points"),
							body: _t("Silahkan pilih customer terlebih dahulu!"),
						});
					}
				}
			});
		},
		show_popup_redeem_loyalty: function() {
			var order = this.pos.get_order();
			if( order ){
				if( order.get_client() && order.get_client().member_status && order.get_client().config_member == 'loyalty' ) {
					this.gui.show_popup('redeem_loyalty_points', {payment_self: this});
				}
			}
		},
		payment_input: function(input) {
			var order = this.pos.get_order();
			// if( order.selected_paymentline.get_freeze_line() ) {
			// 	return;
			// }
			this._super(input);
		}
	});

	var _super_paymentline = models.Paymentline.prototype;
	models.Paymentline = models.Paymentline.extend({
		initialize: function(attributes, options) {
			var self = this;
			_super_paymentline.initialize.apply(this, arguments);
			this.set({
				loyalty_point: 0.00,
				loyalty_amount: 0.00,
			});
		},
		set_loyalty_point: function(points){
			this.set('loyalty_point', points);
		},
		get_loyalty_point: function(){
			return this.get('loyalty_point');
		},
		set_loyalty_amount: function(amount){
			this.set('loyalty_amount', amount);
		},
		get_loyalty_amount: function(){
			return this.get('loyalty_amount');
		},
		set_freeze_line: function(freeze_line){
        	this.set('freeze_line', freeze_line)
        },
        get_freeze_line: function(){
        	return this.get('freeze_line')
        },
	});

});