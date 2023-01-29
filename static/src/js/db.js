odoo.define('marketing_agent.db', function(require) {
    "use strict";

    const PosDB = require('point_of_sale.DB');

    PosDB.include({
        init: function(options) {
            this._super(options);

            this.agent_sorted = [];
            this.agent_by_id = {};
            this.agent_search_string = "";
        },
        _agent_search_string: function(agent) {
            let str = agent.name;

            if( agent.email )   str += '|' + agent.email;

            str = '' + agent.id + ':' + str.replace(':', '') + '\n';
            return str;
        },
        get_agent_by_id: function(id) {
            return this.agent_by_id[id];
        },
        get_agents_sorted: function(max_count) {
            max_count = max_count ? Math.min(this.agent_sorted.length, max_count) : this.agent_sorted.length;
            const agents = [];
            for (let index = 0; index < max_count; index++) {
                agents.push( this.agent_by_id[this.agent_sorted[index]] );
            }
            return agents;
        },
        search_agent: function(query) {
            try {
                query = query.replace(/[\[\]\(\)\+\*\?\.\-\!\&\^\$\|\~\_\{\}\:\,\\\/]/g,'.');
                query = query.replace(/ /g,'.+');
                var re = RegExp("([0-9]+):.*?"+query,"gi");
            } catch {
                return [];
            }
            let results = [];
            for(var i = 0; i < this.limit; i++){
                var r = re.exec(this.agent_search_string);
                if(r){
                    var id = Number(r[1]);
                    results.push(this.get_agent_by_id(id));
                }else{
                    break;
                }
            }
            return results;
        },
        add_agents: function(agents) {
            let _updated_count = 0;

            for (let index = 0; index < agents.length; index++) {
                const agent = agents[index];

                if( !this.agent_by_id[agent.id] ) {
                    this.agent_sorted.push(agent.id)
                }
                this.agent_by_id[agent.id] = agent;
             
                _updated_count += 1;
            }

            if( _updated_count ) {
                this.agent_search_string = "";
                for (const id in this.agent_by_id) {
                    if (Object.hasOwnProperty.call(this.agent_by_id, id)) {
                        const agent = this.agent_by_id[id];
                        this.agent_search_string = this._agent_search_string(agent);
                    }
                }
            }
        },
    })
    return PosDB;
});