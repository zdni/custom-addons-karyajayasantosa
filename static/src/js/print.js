odoo.define('pos_picking_note.print', function(require){
    "use strict";

    var form_widget = require('web.form_widgets');
    var core = require('web.core');
    var _t = core._t;
    var QWeb = core.qweb;

    form_widget.WidgetButton.include({
        on_click: function() {
            if(this.node.attrs.custom === "print_picking_note" ){

                var url = "http://localhost:8000/dotmatrix/print";

                var view = this.getParent();
                var picking_data = view.datarecord.picking_data;
                if (!picking_data){
                    alert('No data to print. Please click Update Printer Data');
                    return;
                }
                console.log(picking_data);

                $.ajax({
                    method: "POST",
                    url: url,
                    data: {
                        printer_data : picking_data
                    },
                    success: function(data) {
                        console.log('Success');
                        console.log(data);
                    },
                    error: function(data) {
                        console.log('Failed');   
                        console.log(data);
                    },
                });
            }
            else{
                this._super();
            }  
        },
    });
});