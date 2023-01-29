odoo.define('marketing_agent.screens', function (require) {
    "use strict";

    const screens = require('point_of_sale.screens');
    const gui = require('point_of_sale.gui');
    const core = require('web.core');

    const QWeb = core.qweb;
    const _t = core._t;

    const MarketingAgentButton = screens.ActionButtonWidget.extend({
        template: "MarketingAgentButton",
        button_click: function() {
            const order = this.pos.get_order();
            if( order.get_orderlines().length ) {
                this.gui.show_screen('marketingagentlist');
            }
        }
    });
    screens.define_action_button({ name: 'marketing_agent_button', widget: MarketingAgentButton});

    const MarketingAgentListScreenWidgetScreenWidget = screens.ScreenWidget.extend({
        template: 'MarketingAgentListScreenWidget',

        init: function(parent, options){
            this._super(parent, options);
            this.agent_cache = new screens.DomCache();
        },

        auto_back: true,

        show: function(){
            const self = this;
            this._super();

            this.renderElement();
            const order = this.pos.get_order()
            this.old_agent = order.get_agent();

            this.$('.back').click(function(){
                self.gui.back();
            });

            this.$('.next').click(function(){   
                self.save_changes();
                self.gui.back();    // FIXME HUH ?
            });

            const agents = this.pos.db.get_agents_sorted(1000);
            this.render_list(agents);

            // this.reload_agents();

            if( this.old_agent ){
                this.toggle_save_button();
            }

            this.$('.marketingagent-list-contents').delegate('.agent-line', 'click', function(event){
                self.line_select(event, $(this), parseInt($(this).data('id')));
            });

            let search_timeout = null;

            if(this.pos.config.iface_vkeyboard && this.chrome.widget.keyboard) {
                this.chrome.widget.keyboard.connect(this.$('.searchbox input'));
            }

            this.$('.searchbox input').on('keypress', function(event){
                clearTimeout(search_timeout);

                const searchbox = this;

                search_timeout = setTimeout(function(){
                    self.perform_search(searchbox.value, event.which === 13);
                }, 70);
            })

            this.$('.searchbox .search-clear').click(function(){
                self.clear_search();
            });
        },
        hide: function() {
            this._super();
            this.new_agent = null;
        },
        perform_search: function(query, associate_result) {
            let agents;
            if(query) {
                agents = this.pos.db.search_agent(query);
                if( associate_result && agents.length == 1 ) {
                    this.new_agent = agents[0];
                    this.save_changes();
                    this.gui.back();
                }
                this.render_list(agents);
            } else {
                agents = this.pos.db.get_agents_sorted(1000);
                this.render_list(agents);
            }
        },
        clear_search: function() {
            const agents = this.pos.db.get_agents_sorted(1000);
            this.render_list(agents);
            this.$('.searchbox input')[0].value = '';
            this.$('.searchbox input').focus();
        },
        render_list: function(agents) {
            let contents = this.$el[0].querySelector('.marketingagent-list-contents');
            contents.innerHTML = '';
            const len = Math.min(agents.length, 1000);
            for (let index = 0; index < len; index++) {
                const agent = agents[index];
                let agentline = this.agent_cache.get_node( agent.id );
                if( !agentline ) {
                    let agentline_html = QWeb.render('AgentLine', { widget: this, agent: agent });
                    agentline = document.createElement('tbody');
                    agentline.innerHTML = agentline_html;
                    agentline = agentline.childNodes[1];
                    this.agent_cache.cache_node( agent.id, agentline );
                }
                if( agent === this.old_agent ) {
                    agentline.classList.add('highlight');
                } else {
                    agentline.classList.remove('highlight');
                }
                contents.appendChild( agentline );
            }
        },
        save_changes: function() {
            const order = this.pos.get_order();
            if( this.has_agent_changed() ) {
                order.set_agent(this.new_agent);
            }
        },
        has_agent_changed: function(){
            if( this.old_agent && this.new_agent ){
                return this.old_agent.id !== this.new_agent.id;
            }else{
                return !!this.old_agent !== !!this.new_agent;
            }
        },
        toggle_save_button: function(){
            var $button = this.$('.button.next');
            if (this.editing_agent) {
                $button.addClass('oe_hidden');
                return;
            } else if( this.new_agent ){
                if( !this.old_agent){
                    $button.text(_t('Set Agent'));
                }else{
                    $button.text(_t('Change Agent'));
                }
            }else{
                $button.text(_t('Deselect Agent'));
            }
            $button.toggleClass('oe_hidden',!this.has_agent_changed());
        },
        line_select: function(event, $line, id){
            var agent = this.pos.db.get_agent_by_id(id);
            this.$('.marketingagent-list .lowlight').removeClass('lowlight');
            if ( $line.hasClass('highlight') ){
                $line.removeClass('highlight');
                $line.addClass('lowlight');
                this.new_agent = null;
                this.toggle_save_button();
            }else{
                this.$('.marketingagent-list .highlight').removeClass('highlight');
                $line.addClass('highlight');
                var y = event.pageY - $line.parent().offset().top;
                this.new_agent = agent;
                this.toggle_save_button();
            }
        },
        close: function(){
            this._super();
            if (this.pos.config.iface_vkeyboard && this.chrome.widget.keyboard) {
                this.chrome.widget.keyboard.hide();
            }
        },
    });
    gui.define_screen({name:'marketingagentlist', widget: MarketingAgentListScreenWidgetScreenWidget});
    
});