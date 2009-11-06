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

jq(function() { 
    statusmessages = jq('#region-content').statusmessages()
    
    arbeitsraum = {
        version : '0.1',
        view_container : jq('.tabbedview_view'),
        searchbox : jq('#tabbedview-searchbox'),
        img_arrow_up : 'icon_open_box.gif',
        img_arrow_down : 'icon_close_box.gif',
        spinner : jq('#tabbedview-spinner'),
        tabs : jq('.tabbedview-tabs').tabs({
            spinner : '',
            cache: false,
            ajaxOptions : {cache: false, 
                           timeout: registry['ftw.tabbedview.interfaces.ITabbedView.timeout'],
                           error: function(XMLHttpRequest, textStatus, errorThrown){
                               statusmessages.error(textStatus + ' <a href="javascript:arbeitsraum.reload_view()">reload</a>');
                           }
                           },
            collapsible: true,
            select : function (e, ui){
                with(arbeitsraum){
                    spinner.show();
                    selected_tab = ui.index;
                    prop('view_name', ui.tab.id);
                    set_url_for_tab(ui.index, ui.tab.id);
                }
             },
             load : function(e, ui){
                  arbeitsraum.spinner.hide();
                  arbeitsraum.view_container.trigger('reload');
             }
        }),
        selected_tab : 0,
        _properties : {},
        _params : {},

        set_url_for_tab : function() {
            var params = this.parse_params();
            this.tabs.tabs('url', this.selected_tab, 'tabbedview_changeview?'+params);        
        },

        reload_view : function() {
            this.set_url_for_tab();
            this.spinner.show();
            this.tabs.tabs('load', this.selected_tab);
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

        flush_params: function() {
            var view = this.prop('view_name');
            if (this._params[view] !== undefined) {
                this._params[view] = {};
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
            var boxes = jq('input[name=uids:list]')
            arbeitsraum.param('selected_count', boxes.length)
            boxes.each(function(el){
                jq(this).attr('checked', true);
                jq('a#select-all').hide()
                // batched
                if (1){
                   jq('#'+arbeitsraum.prop('view_name')+'_overview p#select-folder .selected.counter').html(arbeitsraum.param('selected_count'))   
                   jq('p#select-folder').show() 
                }
                jq('a#select-none').show()
            });
        },
        
        select_none : function(){
            jq('input[name=uids:list]').each(function(el){
                jq(this).attr('checked', false);
                jq('a#select-none').hide()
                jq('a#select-all').show()
                jq('p#select-folder').hide()
            });   
        },
        select_folder :function(){
            jq('#'+arbeitsraum.prop('view_name')+'_overview .listing').animate({'backgroundColor':'yellow'}, 50).animate({'backgroundColor':'white'}, 2000)
            var total = jq('#'+arbeitsraum.prop('view_name')+'_overview p#select-folder .total.counter').html()
            jq('#'+arbeitsraum.prop('view_name')+'_overview p#select-folder .selected.counter').html(total)   
            jq('#'+arbeitsraum.prop('view_name')+'_overview p#select-folder .select-all-text').hide()
        }
    }; 
    
    arbeitsraum.prop('view_name', 'dossiers');
    arbeitsraum.prop('b_size', 50);
    
    jq('.arbeitsraum-tabs .ui-tabs-nav a').removeAttr('title');
      
    arbeitsraum.searchbox.bind("keyup", function(e) {
            var value = arbeitsraum.searchbox.val();
            if (value.length<=3 && arbeitsraum.prop('searchable_text') > value){
                arbeitsraum.prop('searchable_text', '');
                arbeitsraum.flush_params();
                arbeitsraum.reload_view(); 
            }else{
                arbeitsraum.prop('searchable_text', value);
            }
            if (value.length>=3){
                arbeitsraum.flush_params();
                arbeitsraum.reload_view();  
            }
    });
    
    arbeitsraum.view_container.bind('reload', function() {

        /* subview chooser*/
        jq('.ViewChooser a').click(function() {
            arbeitsraum.param('view_name', this.id);
            arbeitsraum.reload_view();
        });
    
    
        /*calander navigation*/
        jq('a.#calendar-previous, a.#calendar-next').click(function(e, o) {
            var month = jq.find_param(this.href)['amp;month:int'];
            var year = jq.find_param(this.href)['year:int'];
            arbeitsraum.param('month:int', month);
            arbeitsraum.param('year:int', year);
            arbeitsraum.reload_view();
            e.preventDefault();
            e.stopPropagation();
        });
        
        /* rollover description */
        /*jq('a.rollover-description').tooltip({ 
            showURL: false,
            track: true, 
            fade: 250
        });*/
        
        /*calendar tooltip*/        
        /*jq('td.event a, td.todayevent a').tooltip({ 
            showURL: false,
            track: true, 
            fade: 250
        });*/
        
        jq('td.event a,  td.todayevent a').click(function(e, o) {
            arbeitsraum.searchbox.val(this.id);
            arbeitsraum.prop('searchable_text', this.id);
            arbeitsraum.param('view_name', 'events');
            arbeitsraum.reload_view();
            e.preventDefault();
            e.stopPropagation();    
        });
        
        /*Sortable*/
        //jq('.sortable').css('padding-right','12px');
        //jq('.sort-selected.sort-reverse').append('<img src="'+arbeitsraum.img_arrow_up+'" style="width:8px;padding-left:0.5em;"/>')
        //jq('.sort-selected.sort-asc').append('<img src="'+arbeitsraum.img_arrow_down+'" style="width:8px;padding-left:0.5em;" />')
        //jq('.sort-selected').css('padding-right','0px');    
            
        jq('.sortable').bind('click', function(e, o) {
           var selected = jq(this);
           var current = jq('#'+arbeitsraum.prop('view_name')+'_overview .sort-selected');
           var sort_order = 'asc';
           if ( selected.attr('id') == current.attr('id')) {
               sort_order = current.hasClass('sort-reverse') ? 'asc': 'reverse';
           }
           arbeitsraum.flush_params();
           arbeitsraum.param('sort_on', this.id);
           arbeitsraum.param('sort_order', sort_order);
           arbeitsraum.reload_view();
        });

        /* Batching */
        jq('.listingBar span a, .listingBar a').click(function(e,o) {
            e.preventDefault();
            e.stopPropagation();
            var obj = jq(this);
            console.log(obj);
            var pagenumber = jq.find_param(this.href).pagenumber
            arbeitsraum.param('pagenumber:int', pagenumber);
            arbeitsraum.reload_view();
        });
        
        /* Visible Types */
        var types_field = jq('#'+arbeitsraum.prop('view_name')+'_overview input.visible_types');
        jq('.arbeitsraum-types li').each(function(index, type) {jq(type).hide();});
        if (types_field.length){
            var types = types_field.val().split(',');
            jq('.arbeitsraum-types li').each(function(index, type) {
                var ty = jq(type);
                var found = 0;
                jq(types).each(function(e, t) {
                    if(ty.attr('class') == t){
                        ty.show();
                    }
                });
            });
        }


    });    
});


