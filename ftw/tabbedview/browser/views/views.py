from datetime import datetime, timedelta
import time
import bisect
from Products.Five.browser import BrowserView
from ftw.table import helper
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter, queryMultiAdapter
from zope.component import queryUtility
from plone.app.content.browser.folderfactories import _allowedTypes
from Products.CMFCore.Expression import getExprContext
from Products.statusmessages.interfaces import IStatusMessage
from zope.component import queryUtility
from ftw.table.interfaces import ITableGenerator
from Products.ATContentTypes.interface import IATTopic
from zope.app.pagetemplate import ViewPageTemplateFile
from plone.app.content.batching import Batch
from plone.memoize import instance
from Acquisition import aq_parent, aq_inner
from zope.component import queryUtility
from opengever.globalsolr.interfaces import ISearch
from collective.solr.flare import PloneFlare
from Acquisition import aq_inner
 
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

    search_index = 'SearchableText'
    show_searchform = True
    sort_on = 'sortable_title'
    sort_order = 'reverse'
    search_options = {}
    depth = -1
    table = None
    batching = ViewPageTemplateFile("batching.pt")
    contents = []

    def __call__(self):
        self.update()
        return super(BaseListingView, self).__call__()

    def update(self):
        self.search()

    def search(self, kwargs):
        pass

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
                                  template = self.table
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
        actions = ai_tool.listActionInfos(object=self.context,
                                          categories=('folder_buttons',))
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

class BaseListingView(ListingView):

    def update(self):
        self.pas_tool = getToolByName(self.context, 'acl_users')
        kwargs = {}

        self.pagesize = 20
        self.pagenumber =  int(self.request.get('pagenumber', 1))
        self.url = self.context.absolute_url()
        if len(self.types):
            kwargs['portal_type'] = self.types
        else:
            kwargs['portal_type'] = self.context.getFriendlyTypes()

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

    def search(self, kwargs):
        catalog = getToolByName(self.context,'portal_catalog')
        if IATTopic.providedBy(self.context):
            contentsMethod = self.context.queryCatalog
        else:
            contentsMethod = self.context.getFolderContents

        self.contents = catalog(path=dict(depth=self.depth, query='/'.join(self.context.getPhysicalPath())), **kwargs)
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

        self.len_results = len(self.contents)

    @property
    @instance.memoize
    def batch(self):
        pagesize = self.pagesize
        b = Batch(self.contents,pagesize=self.pagesize,pagenumber=self.pagenumber)
        return b

class SolrListingView(ListingView):
    
    def build_query(self):
        return self.search_util.buildQuery(**self._search_options)
        
    def update(self):
        self.search_util = queryUtility(ISearch)
        if not self.search_options.has_key('portal_type') and len(self.types):
            self.search_options.update({'portal_type':self.types[0]})
        self.search()

    def search(self, kwargs={}):
        parameters = {}
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
    def __call__(self, view_name=""):
        if view_name:
            self.body_view = queryMultiAdapter((self.context, self.request), name='tabbedview_view-%s' % view_name)
            if self.body_view is None:
                self.body_view = queryMultiAdapter((self.context, self.request), name='tabbedview_view-fallback')
            return super(BrowserView, self).__call__(self.context, self.request)