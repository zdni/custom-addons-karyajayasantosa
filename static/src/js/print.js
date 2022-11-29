odoo.define('pos_z_report.print', function(require){
    "use strict";

    var core = require('web.core');
    var formats = require('web.formats');
    var form_widget = require('web.form_widgets');
    var Model = require('web.DataModel');
    var Session = require('web.Session');
    var utils = require('web.utils');
    
    var round_di = utils.round_decimals;

    var _t = core._t;
    var QWeb = core.qweb;

    form_widget.WidgetButton.include({
        on_click: async function() {
            if(this.node.attrs.custom === "print_z_report" ){
                console.log( 'print_z_report' )
                
                var state = {
                    opening_control   : 'Kontrol Pembukaan',
                    opened            : 'Dalam Proses',
                    closing_control   : 'Kontrol Penutupan',
                    closed            : 'Ditutup & Dikirim',
                }
                
                var view = this.getParent();

                var company = null;
                var config = null;
                var connection_state = false;
                var date = new Date();
                var journals = null;
                var pos = view.datarecord;
                var transactions = {
                    orders: null,
                    returns: null
                };
                var user = null;

                var pos_reference_returns = [];

                var AccountBankStatement = new Model('account.bank.statement');
                var POSOrder = new Model('pos.order');
                var POSConfig = new Model('pos.config');
                var ResUsers = new Model('res.users');
                var ResCompany = new Model('res.company');

                await POSConfig.query(['proxy_ip', 'loyalty_journal_id'])
                    .filter([ ['id', '=', pos.config_id[0]] ])
                    .all()
                    .then( function(data) {
                        if(data) config = data[0];
                    } );
                if( config == null ) return alert('Error: Missing data POS Config');
                
                var url = config.proxy_ip;
                var connection = new Session(undefined,url, { use_cors: true});

                await ResUsers.query(['name', 'company_id'])
                    .filter([ ['id', '=', pos.user_id[0]] ])
                    .all()
                    .then( function(data) {
                        if( data ) user = data[0];
                    } );
                if( user == null ) return alert('Error: Missing data User');

                this.message(connection, 'handsake').then( function(res) {
                    if( res ) connection_state = true;
                }, function(){
                    console.error( 'Tidak bisa mengkoneksikan dengan Proxy' );
                } );

                await ResCompany.query(['email', 'website', 'var', 'name', 'phone', 'currency_id'])
                    .filter([ ['id', '=', user.company_id[0]] ])
                    .all()
                    .then( function(data) {
                        if( data ) company = data[0];
                    } )
                if( company == null ) return alert('Error: Missing data Company');

                await AccountBankStatement.query(['journal_id', 'balance_start', 'balance_end_real'])
                    .filter([ ['id', 'in', pos.statement_ids] ])
                    .all()
                    .then( function( datas ) {
                        if( datas ) {
                            journals = [];
                            _.each( datas, function(data) {
                                if( config.loyalty_journal_id[0] != data.journal_id[0] ){
                                    journals.push( {
                                        name: data.journal_id[1].slice( 0, ((company.currency_id[1].length+2)*-1) ),
                                        total_transaction: data.balance_end_real-data.balance_start,
                                    } );
                                }
                            } )
                        }
                    } );
                if( journals == null ) return alert('Error: Missing data Journal');
                
                await POSOrder.query([])
                    .filter([ ['session_id', '=', pos.id] ])
                    .all()
                    .then( function(datas) {
                        if( datas ) {
                            transactions.orders = {
                                amount: 0,
                                total: 0,
                                total_saving: 0,
                            };
                            transactions.returns = {
                                amount: 0,
                                total: 0,
                            };

                            _.each( datas, function(data) {
                                if( data.amount_total < 0 ) {
                                    transactions.returns.amount = transactions.returns.amount + 1;
                                    transactions.returns.total = transactions.returns.total + data.amount_total;
                                    pos_reference_returns.push( data.pos_reference );
                                }
                                if( data.amount_total > 0 ) {
                                    transactions.orders.amount = transactions.orders.amount + 1;
                                    transactions.orders.total = transactions.orders.total + data.amount_total;
                                    transactions.orders.total_saving = transactions.orders.total_saving + data.total_savings;
                                }
                            } );
                            transactions.total = transactions.orders.total + transactions.returns.total;
                        }
                    } );
                if( transactions.orders == null ) return alert('Error: Missing data Order');

                var receipt = {
                    cashier: user ? user.name : null,
                    company: company,
                    date: `${date.getDate()}-${date.getMonth()}-${date.getFullYear()} ${' '} ${date.getHours()}:${date.getMinutes()}:${date.getSeconds()}`,
                    journals: journals,
                    pos: {
                        cash: {
                            register_balance_end: pos.cash_register_balance_end,
                            register_balance_end_real: pos.cash_register_balance_end_real,
                            register_balance_start: pos.cash_register_balance_start,
                            register_difference: pos.cash_register_difference,
                            register_total_entry_encoding: pos.cash_register_total_entry_encoding,
                        },
                        name: pos.display_name,
                        start_at: pos.start_at,
                        state: state[pos.state],
                        stop_at: pos.stop_at,
                    },
                    transactions: transactions,
                }
                
                console.log( receipt );
                var env = { 
                    receipt: receipt,
                    widget: {
                        format_currency_no_symbol: this.format_currency_no_symbol,
                    } 
                };

                var report = QWeb.render('ZReportReceipt', env);
                if( report ) {
                    this.message(connection, 'print_xml_receipt', { receipt: report }, { timeout: 5000 })
                        .then(function(){
                            console.log('Berhasil Print Z Report');
                        },function(error){
                            if (error) {
                                console.log( error );
                                return;
                            }
                        });
                }

            }
            else{
                this._super();
            }  
        },
        message: function(connection, name, params) {
            return connection.rpc('/hw_proxy/' + name, params || {});
        },
        format_currency_no_symbol: function(amount) {
            if( typeof amount === 'number' ) {
                amount = round_di(amount,2).toFixed(2);
                amount = formats.format_value( round_di(amount, 2), {type: 'float', digits: [69, 2]} );
            }
            return amount;
        }
    });
});