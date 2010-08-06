from Acquisition import aq_inner
from datetime import datetime
from ftw.table import helper
from ftw.table.interfaces import ITableGenerator
from plone.app.content.batching import Batch
from plone.memoize import instance
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.component import queryUtility, getUtility


DEFAULT_ENABLED_ACTIONS = [
    'cut',
    'copy',
    'rename',
    'paste',
    'delete',
    'change_state',
    ]


def sort(list_, index, dir_):
    """sort function used as callback in custom_sort_indexes"""
    reverse = 0
    if dir_ == 'reverse':
        reverse = 1
    return sorted(list_,
                  cmp=lambda x, y: cmp(getattr(x, index), getattr(y, index)),
                  reverse=reverse)


class ListingView(BrowserView):
    """ Base view for listings defining the default values for search
    attributes"""
    types = []

    #columns possible values
    # "<attributename>"
    # ('<attributename>', 'catalog_index')
    # ('<attributename>', callback)
    # ('<attributename>', '<catalog_index>', callback)
    # callback is used to modify the cell attribute.
    # E.g to humanize DateTime objects.
    # The Callback is called with the instance of the current item
    # and the attributename
    columns = (('Title', ),
               ('modified', helper.readable_date), )

    filters = []
    auto_count = None
    custom_sort_indexes = {'Products.PluginIndexes.DateIndex.DateIndex': sort}
    search_index = 'SearchableText'
    show_searchform = True
    sort_on = 'sortable_title'
    sort_order = 'reverse'
    search_options = {}
    depth = -1
    table = None
    batching = ViewPageTemplateFile("batching.pt")
    template = ViewPageTemplateFile("generic.pt")
    contents = []
    request_filters = [('review_state', 'review_state', None)]

    _custom_sort_method = None

    def __init__(self, context, request):
        super(ListingView, self).__init__(context, request)
        registry = getUtility(IRegistry)
        self.pagesize = \
                registry['ftw.tabbedview.interfaces.ITabbedView.batch_size']

    def __call__(self, *args, **kwargs):
        self.update()
        return self.template()

    def update(self):
        raise NotImplementedError('subclass must override this method')

    def search(self, kwargs):
        raise NotImplementedError('subclass must override this method')

    def filters(self):
        return self.filters

    @property
    @instance.memoize
    def batch(self):
        return self.contents

    def show_search_results(self):
        if 'searchable_text' in self.request:
            searchable_text = self.request.get('searchable_text')
            return bool(len(searchable_text))
        return False

    def render_listing(self):
        generator = queryUtility(ITableGenerator, 'ftw.tablegenerator')
        return generator.generate(self.batch,
                                  self.columns,
                                  sortable = True,
                                  selected = (self.sort_on, self.sort_order),
                                  template = self.table,
                                  auto_count = self.auto_count,
                                  )

    def get_css_classes(self):
        if self.show_searchform:
            return ['searchform-visible']
        else:
            return ['searchform-hidden']

    def enabled_actions(self):
        """ Returns a list of enabled actions from portal_actions'
        folder_buttons category.
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
                                          categories=('folder_buttons', ))
        available_action_ids = [a['id'] for a in actions
                                if a['available'] and a['visible']
                                    and a['allowed']]
        return available_action_ids

    def major_actions(self):
        """ Returns a list of major action ids. Theese major actions are listed
        first, the not-listed but available actions (minor actions)
        are listed in a drop-down.
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
        return list(filter(lambda a: a not in major, enabled))

    def buttons(self):
        if callable(self.enabled_actions):
            enabled_actions = list(self.enabled_actions())
        else:
            enabled_actions = list(self.enabled_actions)
        buttons = []
        context = aq_inner(self.context)
        portal_actions = getToolByName(context, 'portal_actions')
        button_actions = portal_actions.listActionInfos(
                            object=context,
                            categories=('folder_buttons', ))
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
        return filter(lambda b: b['id'] in major, self.buttons())

    def minor_buttons(self):
        """ All buttons, which are listed in self.minor_actions
        """
        if callable(self.minor_actions):
            minor = self.minor_actions()
        minor = list(minor)
        return filter(lambda b: b['id'] in minor, self.buttons())

    def setbuttonclass(self, button):
        if button['id'] == 'paste':
            button['cssclass'] = 'standalone'
        else:
            button['cssclass'] = 'context'
        return button

    @property
    def _search_options(self):
        options = {}
        for k, v in self.search_options.items():
            if callable(v):
                v = v(self.context)
            options[k] = v

        return options

    @property
    def view_name(self):
        return self.__name__.split('tabbedview_view-')[1]


class BaseListingView(ListingView):

    def update(self):
        self.pas_tool = getToolByName(self.context, 'acl_users')
        kwargs = {}

        self.pagenumber = int(self.request.get('pagenumber', 1))
        self.url = self.context.absolute_url()
        if len(self.types):
            kwargs['portal_type'] = self.types
#        else:
#            kwargs['portal_type'] = self.context.getFriendlyTypes()

        for f_title, f_request, f_mode in self.request_filters:
            if f_request in self.request:
                result = self.request.get(f_request)
                if len(result):
                    # special handling for the by Month filter
                    if f_mode == 'date':
                        if isinstance(result, list):
                            start = datetime(3000, 1, 1, 0, 0)
                            end = datetime(1970, 1, 1, 0, 0)
                            for item in result:
                                item = item[1: len(item)-1]
                                item = item.split(';')
                                d1 = item[0].split('-')
                                d2 = item[1].split('-')
                                temp_start = datetime(int(d1[0]),
                                                      int(d1[1]),
                                                      int(d1[2]))
                                temp_end = datetime(int(d2[0]),
                                                    int(d2[1]),
                                                    int(d2[2]))
                                if temp_start < start:
                                    start = temp_start
                                if temp_end > end:
                                    end = temp_end
                            kwargs[f_title] = {'query': (start, end),
                                               'range': 'minmax'}

                        else:
                            result = result[1: len(result)-1]
                            result = result.split(';')
                            d1 = result[0].split('-')
                            d2 = result[1].split('-')
                            kwargs[f_title] = {'query': (datetime(
                                                            int(d1[0]),
                                                            int(d1[1]),
                                                            int(d1[2])),
                                                            datetime(
                                                                int(d2[0]),
                                                                int(d2[1]),
                                                                int(d2[2]))),
                                               'range': 'minmax'}
                    else:
                        kwargs[f_title] = result
        if 'searchable_text' in self.request:
            searchable_text = self.request.get('searchable_text')
            if len(searchable_text):
                if searchable_text.endswith('*'):
                    searchable_text = searchable_text
                else:
                    searchable_text = searchable_text+'*'
                kwargs['SearchableText'] = searchable_text

        kwargs['sort_on'] = self.sort_on = self.request.get('sort_on',
                                                            self.sort_on)

        if self.sort_on.startswith('header-'):
            kwargs['sort_on'] = self.sort_on = self.sort_on.split('header-')[1]

        kwargs['sort_order'] = self.sort_order = self.request.get(
                                                    'sort_order',
                                                    self.sort_order)

        #overwrite options with search_options dict on tab
        kwargs.update(self._search_options)
        self.search(kwargs)
        self.post_search(kwargs)

    def build_query(self, *args, **kwargs):
        query = {}
        query.update(kwargs)
        query.update(dict(path=dict(
                            depth=self.depth,
                            query='/'.join(self.context.getPhysicalPath()))))
        sort_on = kwargs.get('sort_on')
        index = self.catalog._catalog.indexes.get(sort_on, None)
        if index is not None:
            index_type = index.__module__
            if index_type in self.custom_sort_indexes:
                del query['sort_on']
                del query['sort_order']
                self._custom_sort_method = \
                    self.custom_sort_indexes.get(index_type)
        return query

    def search(self, kwargs):
        self.catalog = catalog = getToolByName(self.context, 'portal_catalog')
        query = self.build_query(**kwargs)
        self.contents = self.catalog(**query)
        self.len_results = len(self.contents)

    def post_search(self, kwargs):
        #when we're searching recursively we have to remove the current
        # item if its in self.types
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
            self.contents = self._custom_sort_method(self.contents,
                                                     self.sort_on,
                                                     self.sort_order)
        self.len_results = len(self.contents)

    @property
    @instance.memoize
    def batch(self):
        return Batch(self.contents,
                    pagesize=self.pagesize,
                    pagenumber=self.pagenumber)
                    
    @property
    def multiple_pages(self):
        """The multiple_pages in plone.app.batch has a bug 
        if size == pagesize."""

        return len(self.contents) > self.pagesize

