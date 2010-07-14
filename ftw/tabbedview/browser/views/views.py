from datetime import datetime
from Products.Five.browser import BrowserView
from ftw.table import helper
from Products.CMFCore.utils import getToolByName
from zope.component import queryMultiAdapter
from Products.CMFCore.Expression import getExprContext
from ftw.table.interfaces import ITableGenerator
from zope.app.pagetemplate import ViewPageTemplateFile
from plone.app.content.batching import Batch
from plone.memoize import instance
from zope.component import queryUtility
from Acquisition import aq_inner

try:
    from opengever.globalsolr.interfaces import ISearch
    from collective.solr.flare import PloneFlare
except ImportError:
    pass
 
DEFAULT_ENABLED_ACTIONS = [
    'cut',
    'copy',
    'rename',
    'paste',
    'delete',
    'change_state',
    ]


class TabbedView(BrowserView):

    def __init__(self, context, request):
        super(TabbedView, self).__init__(context, request)

    def get_tabs(self):
        return self.get_actions(category='arbeitsraum-tabs')
        #XXX use static tabs for development
        #return [{'id':'dossiers'}, {'id':'documents'}, ]

    def get_actions(self, category=''):
        types_tool = getToolByName(self.context, 'portal_types')
        ai_tool = getToolByName(self.context, 'portal_actionicons')
        actions = types_tool.listActions(object=self.context)
        for action in actions:
            if action.category == category:
                icon = ai_tool.queryActionIcon(action_id=action.id, category=category, context=self.context)
                econtext = getExprContext(self.context, self.context)
                action = action.getAction(ec=econtext)
                if action['available'] and action['visible']:
                    view = self.context.restrictedTraverse("tabbedview_view-%s" % action['id'])
                    yield {
                        'id' : action['id'],
                        'icon' : icon,
                        'url' : action['url'],
                        'class' : ' '.join(view.get_css_classes()),
                        }


    def selected_tab(self):
        return 'Dokumente'

class ListingView(BrowserView):
    types = [] #friendly types
    #columns possible values
    # "<attributename>"
    # ('<attributename>', 'catalog_index')
    # ('<attributename>', callback)
    # ('<attributename>', '<catalog_index>', callback)
    # callback is used to modify the cell attribute E.g to humanize DateTime objects.
    # The Callback is called with the instance of the current item and the attributename
    columns = (('Title',),
               ('modified',helper.readable_date),
               ('Creator',helper.readable_author),)
               
    filters = []
    auto_count = None
    custom_sort_indexes = {}
    search_index = 'SearchableText'
    show_searchform = True
    sort_on = 'sortable_title'
    sort_order = 'reverse'
    search_options = {}
    depth = -1
    table = None
    batching = ViewPageTemplateFile("batching.pt")
    contents = []
    request_filters = [('review_state', 'review_state', None)]
    
    _custom_sort_method = None

    def __call__(self, *args, **kwargs):
        self.update()
        return super(ListingView, self).__call__(*args, **kwargs)

    def update(self):
        raise NotImplementedError('subclass must override this method')

    def search(self, kwargs):
        raise NotImplementedError('subclass must override this method')
        
    def filters(self):
        return self.filters;

    @property
    @instance.memoize
    def batch(self):
        return self.contents

    def show_search_results(self):
        if self.request.has_key('searchable_text'):
            searchable_text = self.request.get('searchable_text')
            return bool(len(searchable_text))
        return False

    def render_listing(self):
        generator = queryUtility(ITableGenerator, 'ftw.tablegenerator')
        return generator.generate(self.batch,
                                  self.columns,
                                  sortable=True,
                                  selected=(self.sort_on, self.sort_order),
                                  template = self.table,
                                  auto_count = self.auto_count,
                                  )

    def get_css_classes(self):
        if self.show_searchform:
            return ['searchform-visible']
        else:
            return ['searchform-hidden']

    def enabled_actions(self):
        """ Returns a list of enabled actions from portal_actions' folder_buttons category.
        The actions will be sorted in order of this list.
        This symbol may be a list (not callable) for easier handling.
        """
        available_action_ids = self.available_actions()
        enabled = []
        for aid in DEFAULT_ENABLED_ACTIONS:
            if aid in available_action_ids:
                enabled.append(aid)
        return enabled

    def available_actions(self):
        """ Returns a list of available action ids
        """
        ai_tool = getToolByName(self.context, 'portal_actions')
        actions = ai_tool.listActionInfos(object=self.context, categories=('folder_buttons',))
        available_action_ids = [a['id'] for a in actions
                                if a['available'] and a['visible'] and a['allowed']
                                ]
        return available_action_ids

    def major_actions(self):
        """ Returns a list of major action ids. Theese major actions are listed
        first, the not-listed but available actions (minor actions) are listed in
        a drop-down.
        This symbol may be a list (not callable) for easier handling.
        """
        if callable(self.enabled_actions):
            return list(self.enabled_actions())
        else:
            return list(self.enabled_actions)

    def minor_actions(self):
        """ Returns a list of auto-generated minor action ids.
        Minor actions are all available actions which are enabled and not
        major actions.
        """
        major = self.major_actions
        major = callable(major) and list(major()) or list(major)
        enabled = self.enabled_actions
        enabled = callable(enabled) and list(enabled()) or list(enabled)
        return list(filter(lambda a:a not in major, enabled))

    def buttons(self):
        if callable(self.enabled_actions):
            enabled_actions = list(self.enabled_actions())
        else:
            enabled_actions = list(self.enabled_actions)
        buttons = []
        context = aq_inner(self.context)
        portal_actions = getToolByName(context, 'portal_actions')
        button_actions = portal_actions.listActionInfos(object=context, categories=('folder_buttons', ))
        # Do not show buttons if there is no data, unless there is data to be
        # pasted
        if not len(self.contents):
            if self.context.cb_dataValid():
                for button in button_actions:
                    if button['id'] == 'paste':
                        return [self.setbuttonclass(button)]
            else:
                return []

        for button in button_actions:
            # Make proper classes for our buttons
            if button['id'] != 'paste' or context.cb_dataValid():
                if button['id'] in enabled_actions:
                    buttons.append(self.setbuttonclass(button))
        return list(buttons)

    def major_buttons(self):
        """ All buttons, which are listed in self.major_actions
        """
        major = self.major_actions
        major = callable(major) and list(major()) or list(major)
        return filter(lambda b:b['id'] in major, self.buttons())

    def minor_buttons(self):
        """ All buttons, which are listed in self.minor_actions
        """
        if callable(self.minor_actions):
            minor = self.minor_actions()
        minor = list(minor)
        return filter(lambda b:b['id'] in minor, self.buttons())

    def setbuttonclass(self, button):
        if button['id'] == 'paste':
            button['cssclass'] = 'standalone'
        else:
            button['cssclass'] = 'context'
        return button
        

    def setbuttonclass(self, button):
        if button['id'] == 'paste':
            button['cssclass'] = 'standalone'
        else:
            button['cssclass'] = 'context'
        return button

    @property
    def _search_options(self):
        options = {}
        for k,v in self.search_options.items():
            if callable(v):
                v = v(self.context)
            options[k] = v
            
        return options

    def get_css_classes(self):
        if self.show_searchform:
            return ['searchform-visible']
        else:
            return ['searchform-hidden']

    @property
    def view_name(self):
        return self.__name__.split('tabbedview_view-')[1]


class BaseListingView(ListingView):

    def update(self):
        self.pas_tool = getToolByName(self.context, 'acl_users')
        kwargs = {}

        self.pagesize = 20
        self.pagenumber =  int(self.request.get('pagenumber', 1))
        self.url = self.context.absolute_url()
        if len(self.types):
            kwargs['portal_type'] = self.types
#        else:
#            kwargs['portal_type'] = self.context.getFriendlyTypes()

        for f_title, f_request, f_mode in self.request_filters:
            if self.request.has_key(f_request):
                result = self.request.get(f_request)
                if len(result):
                    # special handling for the by Month filter
                    #if str(result).startswith('{') and str(result).endswith('}'):
                    if f_mode == 'date':
                        if isinstance(result, list):
                            start = datetime(3000,1,1,0,0)
                            end = datetime(1970,1,1,0,0)
                            for item in result:
                                item = item[ 1: len(item)-1]
                                item = item.split(';')
                                d1 = item[0].split('-')
                                d2 = item[1].split('-')
                                temp_start = datetime(int(d1[0]),int(d1[1]), int(d1[2]))
                                temp_end = datetime(int(d2[0]),int(d2[1]), int(d2[2]))
                                if temp_start < start:
                                    start = temp_start
                                if temp_end > end:
                                    end = temp_end
                            kwargs[f_title] = {'query': (start, end),
                                            'range':'minmax'}
                        
                        else:
                            result = result[ 1: len(result)-1]
                            result = result.split(';')
                            d1 = result[0].split('-')
                            d2 = result[1].split('-')
                            kwargs[f_title] = {'query': (datetime(int(d1[0]),int(d1[1]), int(d1[2])), datetime(int(d2[0]),int(d2[1]), int(d2[2]))),
                                            'range':'minmax'}
                    else:
                        kwargs[f_title] = result
        if self.request.has_key('searchable_text'):
            searchable_text = self.request.get('searchable_text')
            if len(searchable_text):
                searchable_text = searchable_text.endswith('*') and searchable_text or searchable_text+'*'
                kwargs['SearchableText'] = searchable_text

        kwargs['sort_on'] = self.sort_on = self.request.get('sort_on', self.sort_on)

        if self.sort_on.startswith('header-'):
            kwargs['sort_on'] = self.sort_on = self.sort_on.split('header-')[1]

        kwargs['sort_order'] = self.sort_order = self.request.get('sort_order', self.sort_order)

        #overwrite options with search_options dict on tab
        kwargs.update(self._search_options)

        self.search(kwargs)
        self.post_search(kwargs)

    def build_query(self, *args, **kwargs):
        query = {}
        query.update(kwargs)
        query.update(dict(path=dict(depth=self.depth, query='/'.join(self.context.getPhysicalPath()))) )
        sort_on = kwargs.get('sort_on')
        index = self.catalog._catalog.indexes.get(sort_on, None)
        if index is not None:
            index_type = index.__module__            
            if index_type in self.custom_sort_indexes:
                del query['sort_on']
                del query['sort_order']
                self._custom_sort_method = self.custom_sort_indexes.get(index_type)
        return query

    def search(self, kwargs):
        self.catalog = catalog = getToolByName(self.context,'portal_catalog')
        # if IATTopic.providedBy(self.context):
        #     contentsMethod = self.context.queryCatalog
        # else:
        #     contentsMethod = self.context.getFolderContents
        query = self.build_query(**kwargs)
        self.contents = catalog(**query)
        self.len_results = len(self.contents)

    def post_search(self, kwargs):
        #when we're searching recursively we have to remove the current item if its in self.types
        if self.depth != 1 and self.context.portal_type in self.types:
            index = 0
            current_path = '/'.join(self.context.getPhysicalPath())
            for result in self.contents:
                if current_path == result.getPath():
                    self.contents = list(self.contents)
                    self.contents.pop(index)
                    #removing from LazyMap doesn't work
                    #self.contents._len -= 1
                    #self.contents.actual_result_count -= 1
                    #res = self.contents._data.pop(index)
                index +=1
                
        if self._custom_sort_method is not None:
            self.contents = self._custom_sort_method(self.contents, self.sort_on, self.sort_order)
        self.len_results = len(self.contents)
        
    @property
    @instance.memoize
    def batch(self):
        b = Batch(self.contents,pagesize=self.pagesize,pagenumber=self.pagenumber)
        return b

class SolrListingView(ListingView):
    
    sort_on = ''
    
    def build_query(self):
        return self.search_util.buildQuery(**self._search_options)
        
    def update(self):
        self.search_util = queryUtility(ISearch)
        if not self.search_options.has_key('portal_type') and len(self.types):
            self.search_options.update({'portal_type':self.types[0]}) 

        self.search()

    def search(self, kwargs={}):
        
        parameters = {}
        self.sort_on = self.request.get('sort_on', self.sort_on)
        self.sort_order = self.request.get('sort_order', self.sort_order)

        parameters['sort'] = self.sort_on
        if self.sort_on:
            if self.sort_on.startswith('header-'):
                self.sort_on = self.sort_on.split('header-')[1]
                parameters['sort'] = self.sort_on

            if self.sort_order == 'reverse':
                parameters['sort'] = '%s desc' % parameters['sort']
            else:
                parameters['sort'] = '%s asc' % parameters['sort']

        query = self.build_query()
        flares = self.search_util(query, **parameters)
        self.contents = [PloneFlare(f) for f in flares]

class GenericListing(BaseListingView):
    """ uses the tab id for self.types. Good for testing or fallback  """
    def __init__(self, context, request):
        """ kinda ugly way to get things done before GenericListing.__init__"""
        super(BaseListingView, self).__init__(context, request)
        ploneUtils = getToolByName(context, 'plone_utils')
        friendly_types = ploneUtils.getUserFriendlyTypes()
        view_name = self.request.get('view_name', '')
        type_name = view_name.capitalize()
        if type_name in friendly_types:
            self.types = [type_name, ]

        super(GenericListing, self).__init__(context, request)

class FallbackView(BrowserView):
    """ Default Fallback view if no view is registered for the tab """
    def __init__(self, context, request):
        super(FallbackView, self).__init__(context, request)
        self.view_name = 'tabbedview_view-%s' % self.request.get('view_name', '')

class ChangeView(BrowserView):
    """Returns the content for the selected tab. """
    
    template = ViewPageTemplateFile("change.pt")
    
    def __call__(self, view_name=""):
        if view_name:
            self.body_view = queryMultiAdapter((self.context, self.request), name='tabbedview_view-%s' % view_name)
            if self.body_view is None:
                self.body_view = queryMultiAdapter((self.context, self.request), name='tabbedview_view-fallback')
            return self.template()
            
class SelectAllView(BrowserView):
    def __call__(self):
        self.tab = self.context.restrictedTraverse("tabbedview_view-%s" % self.request.get('view_name'))
        self.tab.update()
        
        return super(SelectAllView, self).__call__()
