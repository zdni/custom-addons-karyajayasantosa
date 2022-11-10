odoo.define('config_loyalty_cashback.pos', function (require) {
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
		'config_member',
	]);

	DB.include({
		add_partners: function(partners) {
			var self = this;
			for( var i = 0; i < partners.length; i++ ) {
				var partner = partners[i];
				var old_partner = this.partner_by_id[partner.id];
				if(partners && old_partner && partner.config_member !== old_partner.config_member){
	            	old_partner['config_member'] = partner.config_member;
	            }
			}
			return this._super(partners);
		}
	});



});