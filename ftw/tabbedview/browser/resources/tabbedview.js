/* find_param function */
jQuery.find_param = function(s) {
     var r = {};
     if (s) {
         var q = s.substring(s.indexOf('?') + 1);
         q = q.replace(/\&$/, '');
         jQuery.each(q.split('&'), function() {
             var splitted = this.split('=');
             var key = splitted[0];
             var val = splitted[1];
             if (/^[0-9.]+$/.test(val)) {
                val = parseFloat(val);
             }
             if (val == 'true') {
                val = true;
             }
             if (val == 'false') {
                val = false;
             }
             if (typeof val == 'number' || typeof val == 'boolean' || val.length > 0) {
                r[key] = val;
            }
         });
     }
     return r;
};


/*



*/


statusmessages = {};
statusmessages.error = function(msg){alert(msg)};


jq(function() { 
    /*statusmessages = jq('#region-content').statusmessages()*/
    tabbedview = {
        version : '0.1',
        view_container : jq('.tabbedview_view'),
        searchbox : jq('#tabbedview-searchbox'),
        img_arrow_up : 'icon_open_box.gif',
        img_arrow_down : 'icon_close_box.gif',
        spinner : jq('#tabbedview-spinner'),
        api : {},
        collapsible : false,
        /*tabs : jq('.tabbedview-tabs').tabs({
            spinner : '',
            cache: false,
            ajaxOptions : {cache: false, 
                           timeout: 9999,
                           error: function(XMLHttpRequest, textStatus, errorThrown){
                               statusmessages.error(textStatus + ' <a href="javascript:tabbedview.reload_view()">reload</a>');
                           }
                           },
            collapsible: false,
            select : function (e, ui){
                with(tabbedview){

                    //spinner.show();
                    selected_tab = ui.index;
                    prop('view_name', ui.tab.id);
                    set_url_for_tab();
                }
             },
             load : function(e, ui){
                  tabbedview.spinner.hide();
                  tabbedview.view_container.trigger('reload');
             }
        }),*/
        selected_tab : 0,
        _properties : {},
        _params : {},
        _filters: {},

        set_url_for_tab : function() {
            var params = this.parse_params();
            var url = jq('base').attr('href') 
            var current_tab = jq('.tabbedview-tabs li a.current')
            if( url.substr(url.length-1, 1) == '/'){
                current_tab.attr('href', 'tabbedview_changeview?'+params);        
            }
            else{
                current_tab.attr('href', '/tabbedview_changeview?'+params);  
            }               
        },
        
        reload_view : function() {
            tabbedview.param('initialize', 0);
            var params = this.parse_params();
            var url = jq('base').attr('href') 
            var current_tab = jq('.tabbedview-tabs li a.current')
            jq('#'+tabbedview.prop('view_name')+'_overview').load('tabbedview_changeview?'+params, function(){
                tabbedview.view_container.trigger('reload'); 
            });
            //this.//spinner.show();
        },

        param : function(name, value) {
            var view = this.prop('view_name');
            if (this._params[view] === undefined) {
                this._params[view] = {};
            }
            if ( typeof name === "string" ) {
                if ( value === undefined ) {
                    return this._params[view][name];
                } else {
                    this._params[view][name] = value;
                }
            }
        },
        
        filters : function(name, value) {
            var view = this.prop('view_name');
            if (this._filters[view] === undefined) {
                this._filters[view] = {};
            }
            if ( typeof name === "string" ) {
                if ( value === undefined ) {
                    return this._filters[view][name];
                } else {
                    this._filters[view][name] = value;
                }
            }
        },

        flush_params: function() {
            var view = this.prop('view_name');
            if (this._params[view] !== undefined) {
                this._params[view] = {};
            }
        },

        flush_params: function(value) {
            var view = this.prop('view_name');
            if (this._params[view] !== undefined) {
                delete(this._params[view][value]);
            }
        },

        delete_param: function(filter, value){
            var view = this.prop('view_name');
            if (this._params[view] !== undefined) {
                index = this._params[view][filter].indexOf(value);
                this._params[view][filter].splice(index, 1);
            }
        },
        
        add_param: function(filter, value){
            var view = this.prop('view_name');
            if (this._params[view] !== undefined && this._params[view][filter] !== undefined ) {
                this._params[view][filter].push(value);
            }
            else{
                temp =  [value,];
                this.param(filter, temp);
            }    
        },
        
        parse_params: function() {
            return jq.param(jq.extend(jq.extend({},this._properties), 
                            this._params[this.prop('view_name')]));
        },
        
        prop : function(name, value) {
            if ( typeof name === "string" ) {
                if ( value === undefined ) {
                    return this._properties[name];
                } else {
                    this._properties[name] = value;
                }
            }
        },
        
        select_all : function() {
            var view = this.prop('view_name');
            var boxes = jq('input[name=paths:list]');
            tabbedview.param('selected_count', boxes.length);
            boxes.each(function(el) {
                jq(this).attr('checked', true);
                jq(this).closest('tr').addClass('ui-selected');
            });
            
            var params = this.parse_params();
            var url = jq('base').attr('href')
            if( url.substr(url.length-1, 1) == '/'){
                url = url + '/select_all?'+params;
            }
            else{
                url + '/select_all?'+params;
            }

            jq.ajax({
                url: url,
                success: function(data) {
                    jq('.hidden_items').remove()
                    jq('form[name=tabbedview_form]').append(data);
                }
            });
            
            jq('.tabbedview_select').children('a').each(function(){
                if(jq(this).attr('href').indexOf('tabbedview.select_all()') != -1){
                    jq(this).addClass('selected');
                }
            });
            //jq('.select_folder').show();
        },
        
        select_none : function(){
            jq('input[name=paths:list]').each(function(el) {
                jq(this).attr('checked', false);
                jq(this).closest('tr').removeClass('ui-selected');
            });   
            jq('.select_folder').hide();
            tabbedview.deselect_all()
            
        },
        
        deselect_all :function(){
            jq('.hidden_items').remove()
            jq('.tabbedview_select').children('a').each(function(){
                if(jq(this).attr('href').indexOf('tabbedview.select_all()') != -1){
                    jq(this).removeClass('selected');
                }
            });
        },
        
        select_folder :function() {
            jq('#'+tabbedview.prop('view_name')+'_overview .listing').animate({'backgroundColor':'yellow'}, 50).animate({'backgroundColor':'white'}, 2000);
            var total = jq('#'+tabbedview.prop('view_name')+'_overview p#select-folder .total.counter').html();
            jq('#'+tabbedview.prop('view_name')+'_overview p#select-folder .selected.counter').html(total);
            jq('#'+tabbedview.prop('view_name')+'_overview p#select-folder .select-all-text').hide();
        }
        
    };
    var tabbedview_body =  jq('#tabbedview-body div');
    jQuery.tabbedview = tabbedview
    jq('.tabbedview-tabs').tabs(
        '.panes > div.pane', {
        onBeforeClick: function(e, index){
            var tabbedview = jQuery.tabbedview;
            var current_tab_id = jq('.tabbedview-tabs li a').get(index).id;
            jQuery.tabbedview.param('initialize', 1)
            //spinner.show();
            jQuery.tabbedview.selected_tab = index;
            jQuery.tabbedview.prop('view_name',current_tab_id);
        },
        onClick: function(){
            tabbedview.reload_view();
        }     
    });
    
    tabbedview.tabs_api = jq('.tabbedview-tabs').data('tabs');
    
    if(tabbedview_body.length == 0)return;
    
    var view_name = tabbedview_body.get(0).id.split('_overview')[0]
    tabbedview.prop('view_name', view_name);   
    tabbedview.prop('b_size', 50);
    
    jq('.tabbedview-tabs .ui-tabs-nav a').removeAttr('title');
    
    tabbedview.searchbox.bind("keyup", function(e) {
            var value = tabbedview.searchbox.val();
            if (value.length<=3 && tabbedview.prop('searchable_text') > value) {
                tabbedview.prop('searchable_text', '');
                tabbedview.flush_params('pagenumber:int');
                tabbedview.reload_view(); 
            }else{
                tabbedview.prop('searchable_text', value);
            }
            if (value.length>=3) {
                tabbedview.flush_params();
                tabbedview.reload_view();  
            }
    });
    
    
    
    tabbedview.view_container.bind('reload', function() {
        
        /*sortable*/
        jq('.sortable').bind('click', function(e, o) {
           var selected = jq(this);
           var current = jq('#'+tabbedview.prop('view_name')+'_overview .sort-selected');
           var sort_order = 'asc';
           if ( selected.attr('id') == current.attr('id')) {
               sort_order = current.hasClass('sort-reverse') ? 'asc': 'reverse';
           }
           tabbedview.flush_params();
           tabbedview.param('sort_on', this.id);
           tabbedview.param('sort_order', sort_order);
           tabbedview.reload_view();
        });

    }); 

});


