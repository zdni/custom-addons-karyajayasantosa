odoo.define('pos_z_report.pos', function (require) {
    "use strict";

    var db = require('point_of_sale.DB');
    var models = require('point_of_sale.models');
    var gui = require('point_of_sale.gui');
    var Model = require('web.DataModel');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');

    var QWeb = core.qweb;
    var _t = core._t;

    screens.ProductCategoriesWidget.include({ 
        renderElement: function(){
            var self = this;
            this._super();
            $('#close-session-pos-button').click(function(){
                // self.pos.printZReport()
                self.gui.show_popup('pop_close_session');
            });
        },
    });

    var posmodel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        printZReport: function() {
            console.log( this );
            console.log( this.get_order() );
            var self = this;
            
            var cashier = this.cashier || this.user;
            var company = this.company;
            var date    = new Date();

            var receipt = {
                cashier: cashier ? cashier.name : null,
                company: {
                    email: company.email,
                    website: company.website,
                    company_registry: company.company_registry,
                    contact_address: company.partner_id[1], 
                    vat: company.vat,
                    name: company.name,
                    phone: company.phone,
                    logo:  this.company_logo_base64,
                },
                date: `${date.getDate()}-${date.getMonth()}-${date.getFullYear()} ${date.getHours()}:${date.getMinutes()}:${date.getSeconds()}`,
                pos: {
                    name: this.pos_session.name,
                    status: ( this.pos_session.stop_at ) ? 'Closing' : 'Berjalan',
                    start_at: this.pos_session.start_at,
                    stop_at: this.pos_session.stop_at,
                },
            }
            console.log( receipt );

            // informasi session
            

            // informasi order

            // 
            // var def  = new $.Deferred();
            // // var fields =self.prod_model ? self.prod_model.fields : [];
            // var ctx = {
            //     pricelist: self.pricelist.id,
            //     display_default_code: false,
            // }
            // var fields = ['display_name', 'list_price','price','pos_categ_id', 'taxes_id', 'barcode', 'default_code',  'to_weight', 'uom_id', 'description_sale', 'description', 'product_tmpl_id','tracking']
            // if( !fields.includes('write_date') ) fields.push('write_date');
            // if( !fields.includes('standard_price') ) fields.push('standard_price');

            // new Model('product.product')
            //     .query(fields)
            //     .filter([['sale_ok','=',true],['available_in_pos','=',true],['write_date','>',self.db.get_product_write_date()]])
            //     .context(ctx)
            //     .all({'shadow': true})
            //     .then(function(products){
            //     	self.db.currency_symbol = currency_symbol;
            //         if (self.db.add_products(products)) {
            //             product_list_obj.renderElement(self);
            //             def.resolve();
            //         } else {
            //             def.reject();
            //         }
            //     }, function(err,event){ event.preventDefault(); def.reject(); });    
            // return def;
            var env = {
                pos: this,
                receipt: receipt
            }
            
            // var receipt = QWeb.render('ZReportReceipt', env);
            // this.proxy.print_receipt( receipt );
        },
        // load_server_data: function () {
        //     var self = this;
        //     _.each(this.models, function(model){
        //         if (model && model.model === 'product.product'){
        //             self.prod_model = model;
        //         }
        //     });
        //     return posmodel.load_server_data.apply(this, arguments)
        // },
    });
    
});