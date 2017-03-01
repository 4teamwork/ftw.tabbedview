function Observer(initialValue) {

  var value = initialValue;
  var changed = false;
  var reveal = {};

  function update(newValue) {
    if(newValue === value) {
      changed = false;
    } else {
      changed = true;
    }
    value = newValue;
  }

  function hasChanged() { return changed; }

  reveal.update = update;
  reveal.hasChanged = hasChanged;

  return Object.freeze(reveal);

}

var historyObserver = Observer("");

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
      if (/^[0-9.]{1,16}$/.test(val)) {
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

// Defines the minimum chars required for a search
var search_chars_required = 3;

// Define global baseurl (incl. trailing slash) for later
// functions to use to build absolute URLs.
var baseurl = $('head base').attr('href');
if( baseurl.substr(baseurl.length-1, 1) != '/'){
  baseurl += '/';
}

$(document).bind('tabbedview.unknownresponse', function(event, overview, jqXHR) {
  overview.html($('#tabbedview-msg-unknownresponse').html());
});

load_tabbedview = function(callback) {
  /*statusmessages = $('#region-content').statusmessages()*/

  $.ajaxSetup({
    // Disable caching of AJAX responses
    cache: false
  });

  tabbedview = {
    version : '0.1',
    view_container : $('.tabbedview_view'),
    searchbox : $('#tabbedview-searchbox'),
    img_arrow_up : 'icon_open_box.gif',
    img_arrow_down : 'icon_close_box.gif',
    spinner : $('#tabbedview-spinner'),
    api : {},
    collapsible : false,
    selected_tab : 0,
    _properties : {},
    _params : {},
    _filters: {},

    reload_view : function(callback) {
      var params = this.parse_params();

      // add searchbox text property, when input is prefilled
      // for example, when using the back button
      if (tabbedview.searchbox.val().length >= search_chars_required){
        tabbedview.prop('searchable_text', tabbedview.searchbox.val());
      }

      var current_tab = $('.tabbedview-tabs li a.selected');
      var overview = $('#'+tabbedview.prop('view_name')+'_overview');
      var url = baseurl + 'tabbed_view/listing?ajax_load=1&'+params;
      $.get(url, function(responseText, textStatus, jqXHR){
        if (jqXHR.getResponseHeader('X-Tabbedview-Response') === null) {
          // the response we got does not originate from a tabbed-view
          overview.trigger('tabbedview.unknownresponse', [overview, jqXHR])
          tabbedview.hide_spinner();
          tabbedview.update_tab_menu();
          if (typeof callback == "function"){
            callback(tabbedview);
          }
          return;
        }
        overview.html(responseText);
        // call callback
        if (typeof callback == "function"){
          callback(tabbedview);
        }
        $('#'+tabbedview.prop('old_view_name')+'_overview').html('');

        tabbedview.hide_spinner();
        tabbedview.view_container.trigger('reload');
        tabbedview.update_tab_menu();
      });
      this.show_spinner();
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

    flush_all_params: function() {
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
        var temp =  [value];
        this.param(filter, temp);
      }
    },

    parse_params: function() {
      return $.param($.extend($.extend({},this._properties),
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
      var boxes = $('input.selectable');
      tabbedview.param('selected_count', boxes.length);
      tabbedview.table.ftwtable('select', 'all');

      var params = this.parse_params();
      var url = baseurl+'tabbed_view/select_all?'+params;

      $.ajax({
        url: url,
        success: function(data) {
          $('.hidden_items').remove();
          var table = $('form[name=tabbedview_form] #listing_container');
          var ddata = $(data);
          ddata.find('#above_visibles .hidden_items').insertBefore(table);
          ddata.find('#beneath_visibles .hidden_items').insertAfter(table);
        }
      });

      $('.tabbedview_select').children('a').each(function(){
        if($(this).attr('href').indexOf('tabbedview.select_all()') != -1){
          $(this).addClass('selected');
        }
      });
      //$('.select_folder').show();
    },

    select_none : function(){
      tabbedview.table.ftwtable('deselect', 'all');
      $('.select_folder').hide();
      tabbedview.deselect_all();

    },

    deselect_all :function(){
      $('.hidden_items').remove();
      $('.tabbedview_select').children('a').each(function(){
        if($(this).attr('href').indexOf('tabbedview.select_all()') != -1){
          $(this).removeClass('selected');
        }
      });
    },

    select_folder :function() {
      $('#'+tabbedview.prop('view_name')+'_overview .listing').animate({'backgroundColor':'yellow'}, 50).animate({'backgroundColor':'white'}, 2000);
      var total = $('#'+tabbedview.prop('view_name')+'_overview p#select-folder .total.counter').html();
      $('#'+tabbedview.prop('view_name')+'_overview p#select-folder .selected.counter').html(total);
    $('#'+tabbedview.prop('view_name')+'_overview p#select-folder .select-all-text').hide();
    },

    ie_force_repaint: function() {
      /* insert a dummy div for forcing refresh on IE 7 */
      var $dummy = $('<div>&nbsp;</div>');
      $('#tabbedview-body').prepend($dummy);
      $dummy.remove();
      $('.x-grid-panel').find('>:first').prepend($dummy);
      $dummy.remove();
    },

    show_spinner: function() {
      if (typeof(tabbedview._original_min_height) == 'undefined') {
        tabbedview._original_min_height = $('#content').css('min-height');
      }
      var spinner = tabbedview.spinner;
      if (! spinner.is(':visible')) {
        $('#content').css('min-height', $('#content').height());
        var tab = tabbedview.view_container.find('#tabbedview-body');
        spinner.css('position', 'absolute');
        spinner.css('left', tab.position().left + (tab.width() / 2));
        spinner.css('top', tab.position().top + 50);
        spinner.show();
        tabbedview.ie_force_repaint();
      }
    },

    hide_spinner: function() {
      tabbedview.spinner.hide();
      window.setTimeout(function() {
        if (! tabbedview.spinner.is(':visible')) {
          $('#content').css('min-height', tabbedview._original_min_height);
        }
        tabbedview.ie_force_repaint();
      }, 50);
    },

    update_tab_menu: function() {
      $('.tabbedview-tab-menu > dd').remove();
      var template_class = 'tabbedview-'.concat(tabbedview.prop('view_name')).concat(
          '-menu-items');
      var menu_template = $('.tabbdview-tab-menu-template .'.concat(template_class));

      if (menu_template.length === 0) {
        $('.tabbedview-tab-menu').hide();
      } else {
        $('.tabbedview-tab-menu').show();
        menu_template.clone().appendTo($('.tabbedview-tab-menu'));
      }

      tabbedview.view_container.trigger('tab-menu-updated');
    }

  };
  var tabbedview_body =  $('#tabbedview-body div');
  jQuery.tabbedview = tabbedview;



  /*catch all click events on tabs link elements and call the click method
    because jquery tools tabs doesnt work with plone folderish types*/

  $('.formTab a').click(function(e){
    tabbedview.tabs_api.click($(this).attr('href'));
    e.preventDefault();
    e.stopPropagation();
    return false;
  });


  /* added functionality to the morelink, change the tab in the same way,
     like the normal tab link */
  $('.moreLink a').live('click', function(e){
    tabbedview.tabs_api.click($(this).attr('href'));
    e.preventDefault();
    e.stopPropagation();
    return false;
  });


  /* subview chooser*/
  $('.ViewChooser a').live('click', function(e) {
    e.preventDefault();
    tabbedview.param('view_name', this.id);
    tabbedview.reload_view();
  });


  var initialIndex = 0;
  var initial = $('.formTab .initial');
  if (initial.length > 0) {
    initialIndex = initial.parents('li:first').index();
  }

  /* When a default-tab is configured and we load the tabbedview,
     the jquerytools history triggers a reload event because the
     location.hash is changed from empty string to the name of the
     default tab.
     Now two tabs are loaded: the first tab of the view and the
     configured default-tab. Depending on events-timing and load
     duration the user may be switched to the first tab instead of
     the default tab he configured.
     The fix is to terminate events from jquerytools history regarding
     tab reloading as long as we have no location.hash. This condition
     makes using browser-back / -forward work because in this situation
     we have a location.hash. */
  $('.tabbedview-tabs .formTabs a').bind('history', function(event, hash) {
    historyObserver.update(hash);
    if (!hash) {
      event.preventDefault();
      event.stopPropagation();
    }
    if(historyObserver.hasChanged() && !hash) {
      history.back();
    }
  });

  $('.tabbedview-tabs').tabs(
    '.panes > div.pane', {
        current:'selected',
        history: true,
        initialIndex: initialIndex,
        onBeforeClick: function(e, index){
            if (jQuery.tabbedview.param('initialize') !== 1) {
                /* In some caseses(IE 10) the oneBeforeClick event gets fired
                   multiple times and sometimes with a wrong index. Therefore
                   we add this check which avoid failing whith an javascript
                   error, when trying to get the current tab. */
                if (index >= $('.tabbedview-tabs li a').length){
                  e.preventDefault();
                  return;
                }

                jQuery.tabbedview.view_container.addClass('loading_tab');
                var tabbedview = jQuery.tabbedview;
                if(!index) {
                  index = 0;
                }
                var current_tab_id = $('.tabbedview-tabs li a').get(index).id.split('tab-')[1];

                jQuery.tabbedview.show_spinner();

                jQuery.tabbedview.selected_tab = index;
                var view_name = jQuery.tabbedview.prop('view_name');
                jQuery.tabbedview.prop('old_view_name',view_name);
                jQuery.tabbedview.prop('view_name',current_tab_id);
                jQuery.tabbedview.flush_params('view_name');
                jQuery.tabbedview.param('initialize', 1);
                var tabs = this;
                tabbedview.reload_view(function() {
                    tabs.click(jQuery.tabbedview.selected_tab);
                    jQuery.tabbedview.param('initialize', 0);
                    location.hash = jQuery.tabbedview.prop('view_name');
                    jQuery.tabbedview.view_container.removeClass('loading_tab');
                });
                e.preventDefault();
            }
        }
    });

  tabbedview.tabs_api = $('.tabbedview-tabs').data('tabs');


  if (tabbedview_body.length === 0) {
    return;
  }

  if(location.hash){
    var requested_view_name = location.hash.split('#')[1];
    if($('.tabbedview-tabs li a#tab-' + requested_view_name).length) {
      jQuery.tabbedview.prop('view_name', requested_view_name);
    }
  }

  $('.tabbedview-tabs .ui-tabs-nav a').removeAttr('title');

  tabbedview.searchbox.bind("keyup", $.debounce(250, function(e) {
    var value = tabbedview.searchbox.val();
    var previous_value = tabbedview.prop('searchable_text');
    if (value === tabbedview.searchbox.attr('title')) {
      /* This prevents from reloading when the focus is set on the filter
         field (the field is empty in this state) and then the users switches
         to another applications (which results in setting the title as default
         and after that firing the event). */
      return;
    }

    if (previous_value !== '' && value === previous_value) {
      /* This prevents from reloading when we have key up events which do not
         modify the filter value - for instance when the cursor is moved using
         the keyboard. */
      return;
    }

    if (value.length < search_chars_required && previous_value && previous_value.length > value.length) {
      tabbedview.prop('searchable_text', '');
      tabbedview.flush_params('pagenumber:int');
      tabbedview.reload_view();

    } else {
      tabbedview.flush_params('pagenumber:int');
      tabbedview.prop('searchable_text', value);
    }

    if (value.length >= search_chars_required) {
      tabbedview.flush_params('pagenumber:int');
      if ($('.tab_container').length === 0) {
        tabbedview.reload_view();
      } else {
        tabbedview.show_spinner();
        tabbedview.table.ftwtable('reload');
      }
    }
  }));

  jQuery.tabbedview.show_spinner();

  // batching navigation
  $('.listingBar span a, .listingBar a').live('click', function(e,o) {
    e.preventDefault();
    e.stopPropagation();
    var obj = $(this);
    var pagenumber = $.find_param(this.href).pagenumber;
    tabbedview.param('pagenumber:int', pagenumber);
    tabbedview.reload_view();
  });

  // dynamic batching functionality
  $('#tabbedview-batchbox').live('blur', function() {
    $('#dynamic_batching_form').submit();
  });

  // workaround to bind the submit event with live
  $('body').each(function(){
    $('#dynamic_batching_form').live('submit', function(event){
      tabbedview.param(
        'pagesize', $('#tabbedview-batchbox').val());
      tabbedview.flush_params('pagenumber:int');
      tabbedview.reload_view();
      event.preventDefault();
    });
  });

  tabbedview.view_container.bind('reload', function() {
    //hide or show filter box
    if($('.tabbedview-tabs li a.selected.searchform-hidden').length){
      tabbedview.searchbox.closest('#tabbedview-header').addClass('disabledSearchBox');
      tabbedview.searchbox.closest('.tabbedview_search input').attr('disabled', 'disabled');
    }else{
      tabbedview.searchbox.closest('#tabbedview-header').removeClass('disabledSearchBox');
      tabbedview.searchbox.closest('.tabbedview_search input').removeAttr('disabled');
    }


    //destroy existing table
    if(tabbedview.table){
      tabbedview.table.ftwtable('destroy');
    }
    // initialize new table
    tabbedview.table = $('.tab_container').ftwtable({
      'url': '@@tabbed_view/listing'
    });
  });

  tabbedview.view_container.bind('gridRendered', function() {
    /*sortable*/
    $('th.sortable').bind('click', function(e, o) {
      var selected = $(this);
      var current = $('#'+tabbedview.prop('view_name')+'_overview .sort-selected');
      var sort_order = 'asc';
      if ( selected.attr('id') == current.attr('id')) {
        sort_order = current.hasClass('sort-reverse') ? 'asc': 'reverse';
      }

      tabbedview.flush_params('initialize');
      tabbedview.flush_params('pagenumber:int');
      tabbedview.param('sort', this.id);
      tabbedview.param('dir', sort_order);
      tabbedview.reload_view();
    });

    /* update breadcrumb tooltips */
    $('a.rollover-breadcrumb').tooltip({
      showURL: false,
      track: true,
      fade: 250
    });

    // initalize more-actions menu
    // the initalizeMenues function from plone doesn't work correctly
    jQuery(document).mousedown(actionMenuDocumentMouseDown);

    jQuery('dl.plone-contentmenu-tabbedview-actions').removeClass('activated').addClass('deactivated');

    // add toggle function to header links
    jQuery('dl#plone-contentmenu-tabbedview-actions dt.actionMenuHeader a').
      click(toggleMenuHandler).
      mouseover(actionMenuMouseOver);

    // add hide function to all links in the dropdown, so the dropdown closes
    // when any link is clicked
    jQuery('dl#plone-contentmenu-tabbedview-actions > dd.actionMenuContent').click(hideAllMenus);

    /* actions (<a>) should submit the form */
    $('#tabbedview-menu a.actionicon').click(function(event) {
      if ($(this).attr('href').indexOf('javascript:') === 0) {
        return;

      } else {
        event.preventDefault();
        $(this).parents('form').append($(document.createElement('input')).attr({
          'type' : 'hidden',
          'name' : $(this).attr('href'),
          'value' : '1'
        })).submit();
      }
    });

  });

    tabbedview.set_tab_as_default = function() {
        hideAllMenus();
        var viewname = $.grep(
            $('body').attr('class').split(' '),
            function(name, i) { return name.indexOf('template-') === 0; })[0].split('-')[1];
        var url = baseurl+'@@tabbed_view/set_default_tab';

        $.ajax({
            'url': url,
            cache: false,
            type: 'POST',
            dataType: 'json',
            data: {
                tab: tabbedview.prop('view_name'),
                viewname: viewname},
            success: function(data) {
                tabbedview.show_portal_message(data[0], data[1], data[2]);
            }});
    };

    tabbedview.show_portal_message = function(type, title, message) {
        var cssclass = 'portalMessage '.concat(type);
        var $dt = $('<dt>').text(title);
        var $dd = $('<dd>').html(message);
        var $dl = $('<dl>').attr('class', cssclass);
        $dl.append($dt).append($dd);

        if ($('.portalMessage').length > 0) {
            $dl.insertAfter($('.portalMessage:last'));
        } else if ($('#column-content').length > 0) {
            $('#column-content').prepend($dl);
        } else if ($('#edit-bar').length > 0) {
            $dl.insertAfter($('#edit-bar'));
        }

    };

};
