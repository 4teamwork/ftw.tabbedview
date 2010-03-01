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




jq(function() { 
    statusmessages = jq('#region-content').statusmessages()
    
    arbeitsraum = {
        version : '0.1',
        view_container : jq('.tabbedview_view'),
        searchbox : jq('#tabbedview-searchbox'),
        img_arrow_up : 'icon_open_box.gif',
        img_arrow_down : 'icon_close_box.gif',
        spinner : jq('#tabbedview-spinner'),
        collapsible : false,
        tabs : jq('.tabbedview-tabs').tabs({
            spinner : '',
            cache: false,
            ajaxOptions : {cache: false, 
                           timeout: registry['ftw.tabbedview.interfaces.ITabbedView.timeout'],
                           error: function(XMLHttpRequest, textStatus, errorThrown){
                               statusmessages.error(textStatus + ' <a href="javascript:arbeitsraum.reload_view()">reload</a>');
                           }
                           },
            collapsible: false,
            select : function (e, ui){
                jQuery.History.setHash(ui.tab.id+'-tab');
                with(arbeitsraum){
                    param('initialize', 1)
                    spinner.show();
                    selected_tab = ui.index;
                    prop('view_name', ui.tab.id);
                    set_url_for_tab();
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
        _filters: {},

        set_url_for_tab : function() {
            var params = this.parse_params();
            var url = jq('base').attr('href') 
            if( url.substr(url.length-1, 1) == '/'){
                this.tabs.tabs('url', this.selected_tab, 'tabbedview_changeview?'+params);        
            }
            else{
                this.tabs.tabs('url', this.selected_tab, url + '/tabbedview_changeview?'+params);
            }               
        },
        
        reload_view : function() {
            arbeitsraum.param('initialize', 0);
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
            arbeitsraum.param('selected_count', boxes.length);
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
            
            
            //jq('.select_folder').show();
        },
        
        select_none : function(){
            jq('input[name=paths:list]').each(function(el) {
                jq(this).attr('checked', false);
                jq(this).closest('tr').removeClass('ui-selected');
            });   
            jq('.select_folder').hide();
            deselect_all()
            
        },
        
        deselect_all :function(){
            jq('.hidden_items').remove()
        },
        
        select_folder :function() {
            jq('#'+arbeitsraum.prop('view_name')+'_overview .listing').animate({'backgroundColor':'yellow'}, 50).animate({'backgroundColor':'white'}, 2000);
            var total = jq('#'+arbeitsraum.prop('view_name')+'_overview p#select-folder .total.counter').html();
            jq('#'+arbeitsraum.prop('view_name')+'_overview p#select-folder .selected.counter').html(total);
            jq('#'+arbeitsraum.prop('view_name')+'_overview p#select-folder .select-all-text').hide();
        }
        
    };
    
    var tabbedview_body =  jq('#tabbedview-body div');
    
    if(tabbedview_body.length == 0)return;
    
    var view_name = tabbedview_body.get(0).id.split('_overview')[0].toLowerCase()
    arbeitsraum.prop('view_name', view_name);   
    arbeitsraum.prop('b_size', 50);
    
    jq('.arbeitsraum-tabs .ui-tabs-nav a').removeAttr('title');
    
    arbeitsraum.searchbox.bind("keyup", function(e) {
            var value = arbeitsraum.searchbox.val();
            if (value.length<=3 && arbeitsraum.prop('searchable_text') > value) {
                arbeitsraum.prop('searchable_text', '');
                arbeitsraum.flush_params('pagenumber:int');
                arbeitsraum.reload_view(); 
            }else{
                arbeitsraum.prop('searchable_text', value);
            }
            if (value.length>=3) {
                arbeitsraum.flush_params();
                arbeitsraum.reload_view();  
            }
    });
    
    
    
    arbeitsraum.view_container.bind('reload', function() {
        var tab_id = jQuery.History.getHash().split('-tab')[0]
        if( arbeitsraum.prop('view_name') != tab_id) {
            jq('a[href="#'+tab_id+'_overview"]').trigger('click') ;
        }
        if (jq('#'+arbeitsraum.prop('view_name')).hasClass('searchform-visible')) {
            jq('div.tabbedview_search').show();
        }
        else {
            jq('div.tabbedview_search').hide();
        }
            
        if (!arbeitsraum.filters('auto_filter')){
            arbeitsraum.filters('auto_filter', jq('.testfilter').html())
        }
        else{
            jq('.testfilter').html(arbeitsraum.filters('auto_filter'));
            var view_name = arbeitsraum.prop('view_name')
            jq('.filter_link').each(function(){
                var id = jq(this).attr('id');
                var box = jq(this).parents('.filter_box:first').attr('id');
                if(arbeitsraum._params[view_name][box] != undefined && arbeitsraum._params[view_name][box].indexOf(id) != -1){
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
                            arbeitsraum.deselect_all();
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
        ths = jq('#'+arbeitsraum.prop('view_name')+'_overview .listing th');
        ths2 = jq('#'+arbeitsraum.prop('view_name')+'_overview .journal-listing th');
        jq(jq('#'+arbeitsraum.prop('view_name')+'_overview .listing th').get(0)).width('20px');
        jq(jq('#'+arbeitsraum.prop('view_name')+'_overview .listing th').get(0)).css('padding','0px');
        jq(jq('#'+arbeitsraum.prop('view_name')+'_overview .listing th').get(1)).width('20px');
        jq(jq('#'+arbeitsraum.prop('view_name')+'_overview .listing th').get(1)).css('padding','0px');
        
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
            //console.log(obj);
            var pagenumber = jq.find_param(this.href).pagenumber;
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
        
        /* Filter boxes */
        jq('.filter_link').click(function(){
            value = jq(this).attr('id');
            filter = jq(this).parents('.filter_box:first').attr('id');
            view_name = arbeitsraum.prop('view_name');
            
            if (arbeitsraum._params[view_name]==undefined || arbeitsraum._params[view_name][filter]==undefined){
                temp = [value,];
                arbeitsraum.param(filter, temp);
                arbeitsraum.flush_params('pagenumber:int');
                arbeitsraum.reload_view();
                jq(this).addClass('activate');
            }
            else if(arbeitsraum._params[view_name][filter].indexOf(value) == -1){
                temp = arbeitsraum._params[view_name][filter];
                temp.push(value);
                arbeitsraum.param(filter, temp);
                arbeitsraum.flush_params('pagenumber:int');
                arbeitsraum.reload_view();
                jq(this).addClass('activate');
            }
            else{
                arbeitsraum.delete_param(filter, value);
                arbeitsraum.reload_view();
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
            view_name = arbeitsraum.prop('view_name');
            
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
                arbeitsraum.add_param(filter, value);
            }
            else{
                arbeitsraum.delete_param(filter, value);
            }
        });
        
        /* initalize specally Accordian*/
        var view_name = arbeitsraum.prop('view_name');
        if (arbeitsraum._params[view_name] != undefined){
            var temp = arbeitsraum._params[view_name]['filter_box'];
            if (temp  != undefined){
                arbeitsraum._params[view_name]['filter_box'] = [];
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
    
    jQuery.History.bind(function(){
        var tab_id = jQuery.History.getHash().split('-tab')[0];
        if( arbeitsraum.prop('view_name') != tab_id) {
            jq('a[href="#'+tab_id+'_overview"]').trigger('click') ;
        }

    })
});


 