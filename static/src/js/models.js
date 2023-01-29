odoo.define("marketing_agent.models", function (require) {
    "use strict";

    const models = require('point_of_sale.models');

    models.load_fields('pos.order', 'agent_id');

    models.load_models([
        {
            model: 'res.partner',
            fields: ['name', 'email', 'is_marketing_agent'],
            domain: [['is_marketing_agent','=',true]], 
            loaded: function(self, agents) {
                self.db.add_agents( agents );
            }
        }
    ])

    models.PosModel = models.PosModel.extend({
        get_agent: function() {
            const order = this.get_order();
            if( order ) {
                return order.get_agent();
            }
            return null;
        }
    })

    const _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function() {
			_super_order.initialize.apply(this, arguments);
            
            this.set({ agent: null })
            this.save_to_db();
        },
        init_from_JSON: function(json) {
            _super_order.init_from_JSON.apply(this, arguments);

            let agent;
            if( json.agent_id ) {
                agent = this.pos.db.get_agent_by_id(json.agent_id);
                if (!agent) {
                    console.error('ERROR: trying to load an agent not available in the pos');
                }
            } else {
                agent = null;
            }
            this.set_agent( agent );
        },
        export_as_JSON: function() {
            const json = _super_order.export_as_JSON.apply(this, arguments);
            
            json.agent_id = this.get_agent() ? this.get_agent().id : false;
            return json;
        },
        export_for_printing: function() {
            const receipt = _super_order.export_for_printing.apply(this,arguments);
            const agent = this.get('agent');

            receipt.agent = agent ? agent.name : null;
            return receipt;
        },
        set_agent: function(agent) {
            this.assert_editable();
            this.set('agent', agent);
        },
        get_agent: function() {
            return this.get('agent');
        },
        get_agent_name: function(){
            var agent = this.get('agent');
            return agent ? agent.name : "";
        },
    });
})