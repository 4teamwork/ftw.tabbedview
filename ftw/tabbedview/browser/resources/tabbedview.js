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


statusmessages = {};
statusmessages.error = function(msg){alert(msg);};


load_tabbedview = function() {
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
        selected_tab : 0,
        _properties : {},
        _params : {},
        _filters: {},

        reload_view : function() {
            tabbedview.param('initialize', 0);
            var params = this.parse_params();
            var url = jq('base').attr('href');
            if( url.substr(url.length-1, 1) != '/'){
                url += '/';
            }
            var current_tab = jq('.tabbedview-tabs li a.selected');
            jq('#'+tabbedview.prop('old_view_name')+'_overview').html('');
            jq('#'+tabbedview.prop('view_name')+'_overview').load(url+'tabbed_view/listing?'+params, function(){
                tabbedview.view_container.trigger('reload');
                tabbedview.spinner.hide();
            });
            this.spinner.show();
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
            return null;
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
            return null;
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
                temp =  [value];
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
            return null;
        },

        select_all : function() {
            var view = this.prop('view_name');
            var boxes = jq('input.selectable');
            tabbedview.param('selected_count', boxes.length);
            tabbedview.table.ftwtable('select', 'all');

            var params = this.parse_params();
            var url = jq('base').attr('href').concat('tabbed_view/');

            if( url.substr(url.length-1, 1) == '/'){
                url = url + 'select_all?'+params;
            }
            else{
                url = url + '/select_all?'+params;
            }

            jq.ajax({
                url: url,
                success: function(data) {
                    jq('.hidden_items').remove();
                    var table = jq('form[name=tabbedview_form] table.listing');
                    var ddata = jq(data);
                    ddata.find('#above_visibles .hidden_items').insertBefore(table);
                    ddata.find('#beneath_visibles .hidden_items').insertAfter(table);
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
            tabbedview.table.ftwtable('deselect', 'all');
            jq('.select_folder').hide();
            tabbedview.deselect_all();

        },

        deselect_all :function(){
            jq('.hidden_items').remove();
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
    jQuery.tabbedview = tabbedview;



    /*catch all click events on tabs link elements and call the click method
    because jquery tools tabs doesnt work with plone folderish types*/

    jq('.formTab a').click(function(e){
        tabbedview.tabs_api.click(jq(this).attr('href'));
        location.hash = jq(this).attr('href');
        e.preventDefault();
        e.stopPropagation();

    });

    jq('.tabbedview-tabs').tabs(
        '.panes > div.pane', {
        current:'selected',
        history: true,
        onBeforeClick: function(e, index){
            var tabbedview = jQuery.tabbedview;
            var current_tab_id = jq('.tabbedview-tabs li a').get(index).id;
            jQuery.tabbedview.param('initialize', 1);
            jQuery.tabbedview.spinner.show();
            jQuery.tabbedview.selected_tab = index;
            var view_name = jQuery.tabbedview.prop('view_name');
            jQuery.tabbedview.prop('old_view_name',view_name);
            jQuery.tabbedview.prop('view_name',current_tab_id);
        },
        onClick: function(e, index){
            tabbedview.reload_view();
        }
    });

    tabbedview.tabs_api = jq('.tabbedview-tabs').data('tabs');


    if(tabbedview_body.length == 0)return;

    if(location.hash){
        jQuery.tabbedview.prop('view_name', location.hash.split('#')[1]);
    }

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

    tabbedview.spinner.css('position', 'absolute');
    tabbedview.spinner.show();
    tabbedview.spinner.css('left', '968px');
    tabbedview.spinner.css('top', '140px');



    jq('.listingBar span a, .listingBar a').live('click', function(e,o) {
        e.preventDefault();
        e.stopPropagation();
        var obj = jq(this);
        var pagenumber = jq.find_param(this.href).pagenumber;
        tabbedview.param('pagenumber:int', pagenumber);
        tabbedview.reload_view();
    });
    

    tabbedview.view_container.bind('reload', function() {
        //test global overwrite
        $.fn.ftwtable.defaults.onBeforeLoad = function(){
        };

        // initialize table
        if(Ext.grid){
            if(tabbedview.table){
                tabbedview.table.ftwtable('destroy');
            }
            tabbedview.table = $('#listing_container').ftwtable({
                 'url' : '@@tabbed_view/listing'
            });
        }
        


        // initalize more-actions menu
        // the initalizeMenues function from plone doesn't work correctly
        jQuery(document).mousedown(actionMenuDocumentMouseDown);

        jQuery('dl.plone-contentmenu-tabbedview-actions').removeClass('activated').addClass('deactivated');

        // add toggle function to header links
        jQuery('dl#plone-contentmenu-tabbedview-actions dt.actionMenuHeader a')
            .click(toggleMenuHandler)
            .mouseover(actionMenuMouseOver);

        // add hide function to all links in the dropdown, so the dropdown closes
        // when any link is clicked
        jQuery('dl#plone-contentmenu-tabbedview-actions > dd.actionMenuContent').click(hideAllMenus);

    });
};
