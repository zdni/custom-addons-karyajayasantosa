odoo.define('pos_z_report.popup', function (require) {
    "use strict";

    var PopupWidget = require('point_of_sale.popups');
    var gui = require('point_of_sale.gui');
    var Model = require('web.DataModel');
    // var rpc = require('web.rpc');
    
    var db = require('point_of_sale.DB');
    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');

    var QWeb = core.qweb;
    var _t = core._t;

    var POSSessionClosePopup = PopupWidget.extend({
        template: 'POSSessionClosePopup',
        show: function(options){
            options = options || {};
            this._super(options);
            this.renderElement();
        },
        renderElement: function() {
            this._super();
            var self = this;
            
            $('.close-popup-btn').click(function(){
                self.gui.close_popup();
            });
            $('.close-pos-session').click(function(){
                self.gui.close_popup();
                console.log( self.statement_id )
                if( self.pos.config.cash_control ) {
                    self.gui.show_popup('cash_control',{
                        title:'Closing Cash Control',
                        statement_id:self.statement_id,
                    });
                } // else{
                    // var params = {
                    //     model: 'pos.session',
                    //     method: 'custom_close_pos_session',
                    //     args:[self.pos.pos_session.id]
                    // }
                    // rpc.query(params, {async: false}).then(function(res){
                    //     if(res){
                    //         var cashier = self.pos.get_cashier() || self.pos.user;
                    //         self.gui.close_popup();
                    //         if(self.pos.config.z_report){
                    //             var pos_session_id = [self.pos.pos_session.id];
                    //             self.pos.chrome.do_action('flexiretail_com_advance.pos_z_report',{
                    //                 additional_context:{
                    //                     active_ids:pos_session_id,
                    //                 }
                    //             }).fail(function(e){
                    //                 console.log("Error: ",e);
                    //             });
                    //             if(self.pos.config.iface_print_via_proxy){
                    //                 var report_name = "flexiretail_com_advance.pos_z_thermal_report_template";
                    //                 var params = {
                    //                     model: 'ir.actions.report',
                    //                     method: 'get_html_report',
                    //                     args: [pos_session_id[0], report_name],
                    //                 }
                    //                 rpc.query(params, {async: false})
                    //                 .then(function(report_html){
                    //                     if(report_html && report_html[0]){
                    //                         self.pos.proxy.print_receipt(report_html[0]);
                    //                     }
                    //                 });
                    //             }
                    //             if(cashier && cashier.login_with_pos_screen){
                    //                 setTimeout(function(){
                    //                     framework.redirect('/web/session/logout');
                    //                 }, 5000);
                    //             } else{
                    //                 setTimeout(function(){
                    //                     self.pos.gui.close();
                    //                 }, 5000);
                    //             }
                    //         } else{
                    //             if(cashier && cashier.login_with_pos_screen){
                    //                 framework.redirect('/web/session/logout');
                    //             } else{
                    //                 self.pos.gui.close();
                    //             }
                    //         }
                    //     }
                    // }).fail(function (type, error){
                    //     if(error.code === 200 ){    // Business Logic Error, not a connection problem
                    //        self.gui.show_popup('error-traceback',{
                    //             'title': error.data.message,
                    //             'body':  error.data.debug
                    //        });
                    //     }
                    // });
                // }
            });
        },
    });
    gui.define_popup({name:'pop_close_session', widget: POSSessionClosePopup});

    var CashControlWizardPopup = PopupWidget.extend({
        template : 'CashControlWizardPopup',
        show : async function (options) {
            var self = this;
            options = options || {};
            // this.statement_id = options.statement_id || false;
            var selectedOrder = self.pos.get_order();
            this._super();
            this.renderElement();
            
            $(document).keypress(function (e) {
                if (e.which != 8 && e.which != 46 && e.which != 0 && (e.which < 48 || e.which > 57)) {
                    return false;
                }
            });

            var POSSession = new Model('pos.session');
            
            await POSSession.query([
                'cash_register_balance_start',
                'cash_register_total_entry_encoding',
                'cash_register_balance_end',
                'cash_register_balance_end_real',
                'cash_register_difference'
            ])
                .filter([ ['id', '=', self.pos.pos_session.id] ])
                .all()
                .then( function(data) {
                    if(data){
                        _.each(data, function(value){
                            $("#open_bal").text(self.format_currency(value.cash_register_balance_start));
                            $("#transaction").text(self.format_currency(value.cash_register_total_entry_encoding));
                            $("#theo_close_bal").text(self.format_currency(value.cash_register_balance_end));
                            $("#real_close_bal").text(self.format_currency(value.cash_register_balance_end_real));
                            $("#differ").text(self.format_currency(value.cash_register_difference));
                            $('.button.close_session').show();
                        });
                    }
                } );

            $("#cash_details").show();
            this.$('.button.close_session').hide();
            this.$('.button.ok').click(async function() {
                var dict = [];
                var items=[]
                var cash_details = []
                $(".cashcontrol_td").each(function(){
                    items.push($(this).val());
                });
                while (items.length > 0) {
                  cash_details.push(items.splice(0,3))
                }
                 _.each(cash_details, function(cashDetails){
                    if(cashDetails[2] > 0.00){
                        dict.push({
                           'coin_value':Number(cashDetails[0]),
                           'number':Number(cashDetails[1]),
                           'subtotal':Number(cashDetails[2]),
                           'pos_session_id':self.pos.pos_session.id
                        });
                    }
                });
                if(dict.length > 0){
                    await POSSession
                        .call('cash_control_line', [self.pos.pos_session.id, dict])
                        .then( function(result) {
                            console.log( 'then cash_control_line' )
                            console.log( result )
                        } )
                }
                
                await POSSession.query([
                    'cash_register_balance_start',
                    'cash_register_total_entry_encoding',
                    'cash_register_balance_end',
                    'cash_register_balance_end_real',
                    'cash_register_difference'
                ])
                    .filter([ ['id', '=', self.pos.pos_session.id] ])
                    .all()
                    .then( function(data) {
                        if(data){
                            _.each(data, function(value){
                                $("#open_bal").text(self.format_currency(value.cash_register_balance_start));
                                $("#transaction").text(self.format_currency(value.cash_register_total_entry_encoding));
                                $("#theo_close_bal").text(self.format_currency(value.cash_register_balance_end));
                                $("#real_close_bal").text(self.format_currency(value.cash_register_balance_end_real));
                                $("#differ").text(self.format_currency(value.cash_register_difference));
                                $('.button.close_session').show();
                            });
                        }
                    } );
            });
            this.$('.button.close_session').click(async function() {
                // await POSSession
                //     .call('action_pos_session_close', [ self.pos.pos_session.id ])
                //     .then( function(result) {
                //         console.log( result );
                //     } )
            //     var params = {
            //         model: 'pos.session',
            //         method: 'custom_close_pos_session',
            //         args:[self.pos.pos_session.id]
            //     }
            //     rpc.query(params, {async: false}).then(function(res){
            //         if(res){
            //             var cashier = self.pos.get_cashier();
            //             self.gui.close_popup();
            //             if(self.pos.config.z_report){
            //                 var pos_session_id = [self.pos.pos_session.id];
            //                 self.pos.chrome.do_action('flexiretail_com_advance.pos_z_report',{
            //                     additional_context:{
            //                         active_ids:pos_session_id,
            //                     }
            //                 }).fail(function(e){
            //                     console.log("Error: ",e);
            //                 });
            //                 if(self.pos.config.iface_print_via_proxy){
            //                     var report_name = "flexiretail_com_advance.pos_z_thermal_report_template";
            //                     var params = {
            //                         model: 'ir.actions.report',
            //                         method: 'get_html_report',
            //                         args: [pos_session_id[0], report_name],
            //                     }
            //                     rpc.query(params, {async: false})
            //                     .then(function(report_html){
            //                         if(report_html && report_html[0]){
            //                             self.pos.proxy.print_receipt(report_html[0]);
            //                         }
            //                     });
            //                 }
            //                 if(cashier && cashier.login_with_pos_screen){
            //                     setTimeout(function(){
            //                         framework.redirect('/web/session/logout');
            //                     }, 5000);
            //                 }else{
            //                     setTimeout(function(){
            //                         self.pos.gui.close();
            //                     }, 5000);
            //                 }
            //             } else{
            //                 if(cashier && cashier.login_with_pos_screen){
            //                     framework.redirect('/web/session/logout');
            //                 }else{
            //                     self.pos.gui.close();
            //                 }
            //             }
            //         }
            //     }).fail(function (type, error){
            //         if(error.code === 200 ){    // Business Logic Error, not a connection problem
            //            self.gui.show_popup('error-traceback',{
            //                 'title': error.data.message,
            //                 'body':  error.data.debug
            //            });
            //         }
            //     });
            });
            this.$('.button.cancel').click(function() {
                self.gui.close_popup();
            });
        },
        renderElement: function() {
            var self = this;
            this._super();
            var selectedOrder = self.pos.get_order();
            var table_row = "<tr id='cashcontrol_row'>" +
                            "<td><input type='text'  class='cashcontrol_td coin' id='value' value='0.00' /></td>" + "<span id='errmsg'/>"+
                            "<td><input type='text' class='cashcontrol_td no_of_coin' id='no_of_values' value='0.00' /></td>" +
                            "<td><input type='text' class='cashcontrol_td subtotal' id='subtotal' disabled='true' value='0.00' /></td>" +
                            "<td id='delete_row'><span class='fa fa-trash-o'></span></td>" +
                            "</tr>";
            $('#cashbox_data_table tbody').append(table_row);
            $('#add_new_item').click(function(){
                $('#cashbox_data_table tbody').append(table_row);
            });
            $('#cashbox_data_table tbody').on('click', 'tr#cashcontrol_row td#delete_row',function(){
                $(this).parent().remove();
                self.compute_subtotal();
            });
            $('#cashbox_data_table tbody').on('change focusout', 'tr#cashcontrol_row td',function(){
                var no_of_value, value;
                if($(this).children().attr('id') === "value"){
                    value = Number($(this).find('#value').val());
                    no_of_value = Number($(this).parent().find('td #no_of_values').val());
                }else if($(this).children().attr('id') === "no_of_values"){
                    no_of_value = Number($(this).find('#no_of_values').val());
                    value = Number($(this).parent().find('td #value').val());
                }
                $(this).parent().find('td #subtotal').val(value * no_of_value);
                self.compute_subtotal();
            });
            this.compute_subtotal = function(event){
                var subtotal = 0;
                _.each($('#cashcontrol_row td #subtotal'), function(input){
                    if(Number(input.value) && Number(input.value) > 0){
                        subtotal += Number(input.value);
                    }
                });
                $('.subtotal_end').text(self.format_currency(subtotal));
            }
        }
    });
    gui.define_popup({name:'cash_control', widget: CashControlWizardPopup});
    
});