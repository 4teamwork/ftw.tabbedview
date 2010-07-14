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
            console.log(jq('.tabbedview-tabs').data());
            var url = jq('base').attr('href') 
            if( url.substr(url.length-1, 1) == '/'){
                this.tabs.tabs('url', this.selected_tab, 'tabbedview_changeview?'+params);        
            }
            else{
                this.tabs.tabs('url', this.selected_tab, url + '/tabbedview_changeview?'+params);
            }               
        },
        
        reload_view : function() {
            tabbedview.param('initialize', 0);
            this.set_url_for_tab();
            //this.//spinner.show();
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
    var tabs_api = 2//jq('.tabbedview-tabs').data('tabs');
    var tabbedview_body =  jq('#tabbedview-body div');
    jQuery.tabbedview = tabbedview
    jq('.tabbedview-tabs').tabs(
        '.panes > div', {
        effect: 'ajax',
        onBeforeClick: function(e, index){
            var tabbedview = jQuery.tabbedview;
            var current_tab_id = jq('.tabbedview-tabs li a').get(index).id;
            jQuery.tabbedview.param('initialize', 1)
            //spinner.show();
            jQuery.tabbedview.selected_tab = index;
            jQuery.tabbedview.prop('view_name',current_tab_id);
            //jQuery.tabbedview.set_url_for_tab();
        }     
    });
    
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
        /*var tab_id = jQuery.History.getHash().split('-tab')[0]
        if( tabbedview.prop('view_name') != tab_id) {
            jq('a[href="#'+tab_id+'_overview"]').trigger('click') ;
        }
        if (jq('#'+tabbedview.prop('view_name')).hasClass('searchform-visible')) {
            jq('div.tabbedview_search').show();
        }
        else {
            jq('div.tabbedview_search').hide();
        }
            */
        if (!tabbedview.filters('auto_filter')){
            tabbedview.filters('auto_filter', jq('.testfilter').html())
        }
        else{
            jq('.testfilter').html(tabbedview.filters('auto_filter'));
            var view_name = tabbedview.prop('view_name')
            jq('.filter_link').each(function(){
                var id = jq(this).attr('id');
                var box = jq(this).parents('.filter_box:first').attr('id');
                if(tabbedview._params[view_name][box] != undefined && tabbedview._params[view_name][box].indexOf(id) != -1){
                    jq(this).addClass('activate');
                }
                else{
                    jq(this).removeClass('activate');
                }
            });
        }

        /* selectable */
        
        jq('.tabbedview-tabs .listing').selectable({
                        filter:'tr:gt(0)', 
                        cancel: 'a, input, th',
                        selecting: function(event, ui) {
                            jq('input[name="paths:list"]', ui.selecting).attr('checked', true);
                        },
                        selected: function(event, ui) {
                            jq('.ui-selected input[name="paths:list"]').attr('checked', true);
                        },
                        unselecting: function(event, ui) {
                            jq('input[name="paths:list"]', ui.selecting).attr('checked', false);
                            tabbedview.deselect_all();
                        }
                            
        });

        /* checkboxes */
        jq('input[name="paths:list"]').click(function(){
            var checkbox = jq(this);
            if (checkbox.attr('checked')) {
                checkbox.closest('tr').addClass('ui-selected');
            }
            else {
                checkbox.closest('tr').removeClass('ui-selected');
            }
        });
        
        /* draggable */
        jq("span.draggable").draggable({
        			                cursor: 'move',
        			                cursorAt: { top: -10, left: -10 },
        			                helper: function(event) {
        				                return jq('<div class="ui-widget-header">'+jq('tr.ui-selected').length+' Objekte verschieben</div>');
        			                }
        });
        
        
        

        /* resizeable */
        ths = jq('#'+tabbedview.prop('view_name')+'_overview .listing th');
        ths2 = jq('#'+tabbedview.prop('view_name')+'_overview .journal-listing th');
        jq(jq('#'+tabbedview.prop('view_name')+'_overview .listing th').get(0)).width('20px');
        jq(jq('#'+tabbedview.prop('view_name')+'_overview .listing th').get(0)).css('padding','0px');
        jq(jq('#'+tabbedview.prop('view_name')+'_overview .listing th').get(1)).width('20px');
        jq(jq('#'+tabbedview.prop('view_name')+'_overview .listing th').get(1)).css('padding','0px');
        
        ths.filter(':lt('+(ths.length-1)+'):gt(1)').resizable({ 
            handles: 'e',
            resize: function(event, ui) {
                nextElement = ui.element.next();
                if (!self._nextOrigSize) {
                    self._nextOrigSize = nextElement.width();  
                }
                nextElement.width(self._nextOrigSize - (ui.size.width - ui.originalSize.width));
            },
            stop: function(event, ui) {
                self._nextOrigSize = null;
            }
        });
        
        ths2.filter(':lt('+(ths2.length-1)+')').resizable({ 
            handles: 'e',
            resize: function(event, ui) {
                nextElement = ui.element.next();
                if (!self._nextOrigSize) {
                    self._nextOrigSize = nextElement.width();  
                }
                nextElement.width(self._nextOrigSize - (ui.size.width - ui.originalSize.width));
            },
            stop: function(event, ui) {
                self._nextOrigSize = null;
            }
        });


        /* subview chooser*/
        jq('.ViewChooser a').click(function() {
            tabbedview.param('view_name', this.id);
            tabbedview.reload_view();
        });
    
    
        /*calander navigation*/
        jq('a.#calendar-previous, a.#calendar-next').click(function(e, o) {
            var month = jq.find_param(this.href)['amp;month:int'];
            var year = jq.find_param(this.href)['year:int'];
            tabbedview.param('month:int', month);
            tabbedview.param('year:int', year);
            tabbedview.reload_view();
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
            tabbedview.searchbox.val(this.id);
            tabbedview.prop('searchable_text', this.id);
            tabbedview.param('view_name', 'events');
            tabbedview.reload_view();
            e.preventDefault();
            e.stopPropagation();    
        });
        
        /*Sortable*/
        //jq('.sortable').css('padding-right','12px');
        //jq('.sort-selected.sort-reverse').append('<img src="'+tabbedview.img_arrow_up+'" style="width:8px;padding-left:0.5em;"/>')
        //jq('.sort-selected.sort-asc').append('<img src="'+tabbedview.img_arrow_down+'" style="width:8px;padding-left:0.5em;" />')
        //jq('.sort-selected').css('padding-right','0px');    
            
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

        /* Batching */
        jq('.listingBar span a, .listingBar a').click(function(e,o) {
            e.preventDefault();
            e.stopPropagation();
            var obj = jq(this);
            var pagenumber = jq.find_param(this.href).pagenumber;
            tabbedview.param('pagenumber:int', pagenumber);
            tabbedview.reload_view();
        });
        
        /* Visible Types */
        var types_field = jq('#'+tabbedview.prop('view_name')+'_overview input.visible_types');
        jq('.tabbedview-types li').each(function(index, type) {jq(type).hide();});
        if (types_field.length){
            var types = types_field.val().split(',');
            jq('.tabbedview-types li').each(function(index, type) {
                var ty = jq(type);
                var found = 0;
                jq(types).each(function(e, t) {
                    if(ty.attr('class') == t){
                        ty.show();
                    }
                });
            });
        }
        
        /* Filter boxes */
        jq('.filter_link').click(function(){
            value = jq(this).attr('id');
            filter = jq(this).parents('.filter_box:first').attr('id');
            view_name = tabbedview.prop('view_name');
            
            if (tabbedview._params[view_name]==undefined || tabbedview._params[view_name][filter]==undefined){
                temp = [value,];
                tabbedview.param(filter, temp);
                tabbedview.flush_params('pagenumber:int');
                tabbedview.reload_view();
                jq(this).addClass('activate');
            }
            else if(tabbedview._params[view_name][filter].indexOf(value) == -1){
                temp = tabbedview._params[view_name][filter];
                temp.push(value);
                tabbedview.param(filter, temp);
                tabbedview.flush_params('pagenumber:int');
                tabbedview.reload_view();
                jq(this).addClass('activate');
            }
            else{
                tabbedview.delete_param(filter, value);
                tabbedview.reload_view();
                jq(this).removeClass('activate');
            }
        });
        
        /* filterboxes as Accordian*/
        
        /* XXX THE STANDARD ACCORDION CAN ONLY SHOW ONE ITEM AT ONCE WE NEED MUTLTIPLE
        jq('.filters').accordion({ autoHeight: false, collapsible: true, active:2, animated: false, navigation: true  }); */
        
        /* filterboxes as specally Accordian*/
        //jq('.testfilter').accordion({ autoHeight: false, collapsible: true, active:2, animated: false, navigation: true  });
        
        /* filterboxes with specally Accordian*/
        jq('.ui-accordion-header').click(function(){
            value = jq(this).attr('id');
            filter = 'filter_box';
            view_name = tabbedview.prop('view_name');
            
            /* Toogle css classes*/
            jq(this).children('.ui-icon').toggleClass('ui-icon-triangle-1-e');
            jq(this).children('.ui-icon').toggleClass('ui-icon-triangle-1-s');
            jq(this).toggleClass('ui-state-active');
            jq(this).toggleClass('ui-corner-all');
            jq(this).toggleClass('ui-corner-top');
            
            /*toggle div*/
            jq(this).next().toggle();
            
            /*save it in params*/
            if(jq(this).hasClass('ui-state-active')){
                tabbedview.add_param(filter, value);
            }
            else{
                tabbedview.delete_param(filter, value);
            }
        });
        
        /* initalize specally Accordian*/
        var view_name = tabbedview.prop('view_name');
        if (tabbedview._params[view_name] != undefined){
            var temp = tabbedview._params[view_name]['filter_box'];
            if (temp  != undefined){
                tabbedview._params[view_name]['filter_box'] = [];
                for(var i=0;i<temp.length;i++) {
                    var id = temp[i];
                    jq('#'+id).click();
                }
            }
        }

        /* actions (<a>) should submit the form */
        jq('.buttons a.listing-button').click(function(event) {
          event.preventDefault();
          jq(this).parents('form').append(jq(document.createElement('input')).attr({
            'type' : 'hidden',
            'name' : jq(this).attr('href'),
            'value' : '1'
          })).submit();
         });
        
    }); 
    
    /*jQuery.History.bind(function(){
        var tab_id = jQuery.History.getHash().split('-tab')[0];
        if( tabbedview.prop('view_name') != tab_id) {
            jq('a[href="#'+tab_id+'_overview"]').trigger('click') ;
        }

    })*/
});


