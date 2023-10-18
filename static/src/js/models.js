odoo.define("deposit_customer.models", function(require) {
    "use strict";

    var DB = require('point_of_sale.DB');
    var models = require("point_of_sale.models");

    models.load_fields('res.partner', ['total_deposit']);
    
	DB.include({
		add_partners: function(partners) {
			console.log("add_partners");
			for( var i = 0; i < partners.length; i++ ) {
				var partner = partners[i];
				var old_partner = this.partner_by_id[partner.id];
				if(partners && old_partner && partner.total_deposit !== old_partner.total_deposit){
	            	old_partner['total_deposit'] = partner.total_deposit;
	            }
			}
			return this._super(partners);
		}
	});
    
    // return models;
})