from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from ftw.dictstorage.interfaces import IDictStorage
from ftw.tabbedview import tabbedviewMessageFactory as _
from ftw.tabbedview.interfaces import IGridStateStorageKeyGenerator
from ftw.tabbedview.interfaces import IListingView
from ftw.table.basesource import BaseTableSourceConfig
from ftw.table.catalog_source import DefaultCatalogTableSourceConfig
from ftw.table.interfaces import ITableGenerator
from ftw.table.interfaces import ITableSource
from plone.memoize import instance
from plone.registry.interfaces import IRegistry
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import queryMultiAdapter
from zope.component import queryUtility, getUtility, getMultiAdapter
from zope.interface import implements
import pkg_resources


try:
    # plone >= 4.3
    pkg_resources.get_distribution('plone.batching')
    from plone.batching import Batch
    batch_method = Batch.fromPagenumber

except pkg_resources.DistributionNotFound:
    # plone < 4.3
    from plone.app.content.batching import Batch
    batch_method = Batch

try:
    import json
except ImportError:
    import simplejson as json


DEFAULT_ENABLED_ACTIONS = [
    'cut',
    'copy',
    'rename',
    'paste',
    'delete',
    'change_state',
    ]


_marker = object()


class ListingView(BrowserView, BaseTableSourceConfig):
    """ Base view for listings defining the default values for search
    attributes"""
    implements(IListingView)

    # see ftw.table documentation on how columns work
    columns = ()

    # additional options to pass to ftw.table:
    table_options = None

    # change the template used by ftw.table:
    table_template = None

    show_searchform = True
    show_selects = True
    show_menu = True
    depth = -1
    batching = ViewPageTemplateFile("batching.pt")
    menu = ViewPageTemplateFile("menu.pt")
    selection = ViewPageTemplateFile("selection.pt")
    template = ViewPageTemplateFile("generic.pt")
    select_all_template = ViewPageTemplateFile('select_all.pt')
    batching_enabled = True
    contents = []
    groupBy = None
    use_batch = True

    def __init__(self, context, request):
        super(ListingView, self).__init__(context, request)
        registry = getUtility(IRegistry)
        self.pagesize = \
            registry['ftw.tabbedview.interfaces.ITabbedView.batch_size']
        self.extjs_enabled = False

        self.dynamic_batchsize_enabled = registry[
            'ftw.tabbedview.interfaces.ITabbedView.dynamic_batchsize_enabled']

        self.max_dynamic_batchsize = registry[
            'ftw.tabbedview.interfaces.ITabbedView.max_dynamic_batchsize']

        if self.table_options is None:
            self.table_options = {}

    def __call__(self, *args, **kwargs):
        config_view = self.context.restrictedTraverse('@@tabbedview_config')
        self.extjs_enabled = config_view.extjs_enabled(self)

        # XXX : we need to be able to detect a extjs update request and return
        # only the template without data, because a later request will update
        # the table with json.
        # better approach to implement: create a new extjs-update-view witch
        # returns a json containing the template with data and the data as
        # json.

        if self.extjs_enabled:
            if ('tableType' in self.request and
                    self.request['tableType'] == 'extjs'):
                self.update()
                # add addition html that will be injected in the view
                static = {'batching': '<!--iefix-->',
                          'menu': '<!--iefix-->',
                          'selection': '<!--iefix-->'}
                if self.use_batch:
                    static['batching'] = self.batching()
                if self.contents:
                    static['menu'] = self.menu()
                    static['selection'] = self.selection()

                self.table_options.update({'static': static})
                # Set correct content type for JSON response
                self.request.response.setHeader("Content-type",
                                                "application/json")
                return self.render_listing()
            else:
                self.contents = [{}, ]
                self.load_request_parameters()
                # We're returning a HTML *fragment*, therefore prevent
                # Diazio from theming it
                self.request.response.setHeader('X-Theme-Disabled', 'True')
                return self.template()

        self.update()
        return self.template()

    def load_request_parameters(self):
        """Load parameters such as page or filter from request.
        """

        # load the groupBy parameter
        self.groupBy = self.request.get('groupBy', None)

        #if the grid is in dragging mode we dont use a batch ans set depth to 1
        if self.request.get('sort', '') == 'draggable':
            self.use_batch = False
            self.depth = 1

        if self.use_batch:
            # pagenumber
            self.batching_current_page = int(self.request.get('pagenumber', 1))
            # XXX eliminate self.pagenumber
            self.pagenumber = self.batching_current_page

            # dynamic batching
            if self.dynamic_batchsize_enabled:
                if self.request.get('pagesize', None):
                    try:
                        self.pagesize = int(self.request.get('pagesize'))
                    except ValueError:
                        pass

                    if self.max_dynamic_batchsize < self.pagesize:
                        self.pagesize = self.max_dynamic_batchsize

            self.batching_pagesize = self.pagesize

        # set url
        self.url = self.context.absolute_url()

        # filtering
        if 'searchable_text' in self.request:
            self.filter_text = self.request.get('searchable_text')

        # ordering
        self.sort_on = self.request.get('sort', self.sort_on)
        if self.sort_on.startswith('header-'):
            self.sort_on = self.sort_on.split('header-')[1]

        # reverse
        default_sort_order = self.sort_reverse and 'reverse' or 'asc'
        sort_order = self.request.get('dir', default_sort_order)
        self.sort_order = {'ASC': 'asc',
                           'DESC': 'reverse'}.get(sort_order, sort_order)

        self.sort_reverse = self.sort_order == 'reverse'

    def update(self):
        self.load_request_parameters()

        # load the grid state
        self.load_grid_state()

        # build the query
        query = self.table_source.build_query()

        # search
        results = self.table_source.search_results(query)
        results = self.custom_sort(results, self.sort_on, self.sort_reverse)

        if self.groupBy:
            # lets group the results. this will change the structure of the
            # results list: rows are now wrapped in a tuple...

            # groupBy contains the search index of the column - we need to
            # have the processed column now...
            generator = queryUtility(ITableGenerator, 'ftw.tablegenerator')
            columns = generator.process_columns(self.columns)

            column = None
            for col in columns:
                if col['sort_index'] == self.groupBy:
                    column = col
                    break

            if not column:
                raise RuntimeError('Could not find sort_index "%s"' % \
                                       self.groupBy + \
                                       ' in this tab configuration.')

            # now lets group it with the table source adapter
            results = self.table_source.group_results(results, column)

        self.contents = results

        # post search
        self.post_search(query)

    def custom_sort(self, results, sort_on, sort_reverse):
        """Custom sort method.
        """

        if getattr(self, '_custom_sort_method', None) is not None:
            results = self._custom_sort_method(results, sort_on, sort_reverse)

        return results

    def post_search(self, query):
        pass

    @property
    def table_source(self):
        try:
            return self._table_source
        except AttributeError:
            self._table_source = getMultiAdapter((self, self.request),
                                                 ITableSource)
            return self._table_source

    def show_search_results(self):
        if 'searchable_text' in self.request:
            searchable_text = self.request.get('searchable_text')
            return bool(len(searchable_text))
        return False

    def render_listing(self):
        generator = queryUtility(ITableGenerator, 'ftw.tablegenerator')
        if self.extjs_enabled:
            output = 'json'
        else:
            output = 'html'
        rows = []
        if self.use_batch:
            rows = self.batch
        else:
            #if the view is grouped or in dragging mode we disable batching
            rows = self.contents

        return generator.generate(rows,
                                  self.columns,
                                  sortable=True,
                                  selected=(self.sort_on, self.sort_order),
                                  template=self.table_template,
                                  options=self.table_options,
                                  output=output
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
        minor = self.minor_actions
        if callable(minor):
            minor = minor()
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

    def select_all(self, pagenumber, selected_count):
        """Called when select-all is clicked. Returns HTML containing
        a hidden input field for each field which is not displayed at
        the moment.

        `pagenumber`: the current page number (1 is first page)
        `selected_count`: number of items selected / displayed on this page
        """

        if not self.batching_enabled:
            return

        if self.table_options is None:
            self.table_options = {}

        self.update()

        above, beneath = self._select_all_remove_visibles(
            self.contents, pagenumber, selected_count)
        return self.select_all_template(above=above, beneath=beneath)

    def _select_all_remove_visibles(self, contents, pagenumber,
                                    selected_count):
        """Helper method for removing all items which are displayed at the
        moment. Returns a tuple of two lists containing elements which
        should be above the visibles and elements which should be beneath
        the visibles.

        `contents`: list of all items
        `pagenumber`: the current page number (1 is first page)
        `selected_count`: number of items selected / displayed on this page
        """

        contents = list(contents)

        start_hidden = (pagenumber - 1) * self.pagesize
        end_hidden = start_hidden + selected_count

        return contents[0:start_hidden], contents[end_hidden:]

    @property
    @instance.memoize
    def batch(self):

        return batch_method(self.contents,
                            pagesize=self.pagesize,
                            pagenumber=self.pagenumber)

    @property
    def multiple_pages(self):
        """The multiple_pages in plone.app.batch has a bug
        if size == pagesize."""
        if not self.use_batch:
            return 0
        return len(self.contents) > self.pagesize

    def load_grid_state(self):
        """Loads the stored grid state - if any is stored.
        """
        # get the key from the key generator
        generator = queryMultiAdapter((self.context, self, self.request),
                                      IGridStateStorageKeyGenerator)

        key = generator.get_key()

        # get the state (string)
        storage = IDictStorage(self)
        state = storage.get(key, None)

        if state:
            parsed_state = json.loads(state)

            # Do not persistently store grouping, since loading the group
            # initially would not work.
            if 'group' in parsed_state:
                del parsed_state['group']

            # In some situations the sorting in the state is corrupt. Every
            # visible row should have a 'sortable' by default.
            column_state_by_id = dict((col['id'], col)
                                      for col in parsed_state['columns'])

            for column in self.columns:
                if not isinstance(column, dict):
                    continue

                name = column.get('sort_index', column.get('column', None))
                if name not in column_state_by_id:
                    continue

                col_state = column_state_by_id[name]
                if 'sortable' not in col_state:
                    col_state['sortable'] = True

            state = json.dumps(parsed_state)

        if state:
            self.table_options.update({'gridstate': state})
        else:
            return

        # if the sorting order is set in the state and is not set in the
        # request, we need to change it in the config using the state
        # config.
        if self.request.get('dir', _marker) == _marker and \
                self.request.get('sort', _marker) == _marker and \
                'sort' in parsed_state:
            if 'field' in parsed_state['sort']:
                self.sort_on = parsed_state['sort']['field']
            if parsed_state['sort']['direction'] == 'ASC':
                self.sort_order = 'asc'
                self.sort_reverse = False
            else:
                self.sort_order = 'reverse'
                self.sort_reverse = True

    def update_tab_actions(self, actions):
        # XXX: This method is used from tabbed.py, which does not call this
        # view. This means, that the class variable extjs_enable is still False
        # although extjs is enabled.
        config_view = self.context.restrictedTraverse('@@tabbedview_config')
        extjs_enabled = config_view.extjs_enabled(self)

        if extjs_enabled:
            actions.append({
                    'label': _(u'Reset table configuration'),
                    'href': 'javascript:reset_grid_state()',
                    'description': _(u'Resets the table configuration for this tab.')
                    })

        return actions


class CatalogListingView(ListingView, DefaultCatalogTableSourceConfig):

    # modify the base catalog query. This will be
    search_options = {}

    def update_config(self):
        DefaultCatalogTableSourceConfig.update_config(self)

        # configuration for the extjs grid
        extjs_conf = {'auto_expand_column': 'sortable_title'}
        if self.extjs_enabled and isinstance(self.table_options, dict):
            self.table_options.update(extjs_conf)
        elif self.table_options is None:
            self.table_options = extjs_conf.copy()

        # search in current context by default
        self.filter_path = '/'.join(self.context.getPhysicalPath())
