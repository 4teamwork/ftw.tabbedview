from Acquisition import aq_inner
from ftw.table.catalog_source import DefaultCatalogTableSourceConfig
from ftw.table.basesource import BaseTableSourceConfig
from ftw.table.interfaces import ITableSource
from ftw.table.interfaces import ITableGenerator
from plone.app.content.batching import Batch
from plone.memoize import instance
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.component import queryUtility, getUtility, getMultiAdapter


DEFAULT_ENABLED_ACTIONS = [
    'cut',
    'copy',
    'rename',
    'paste',
    'delete',
    'change_state',
    ]


class ListingView(BrowserView, BaseTableSourceConfig):
    """ Base view for listings defining the default values for search
    attributes"""

    # see ftw.table documentation on how columns work
    columns = ()

    # additional options to pass to ftw.table:
    table_options = None

    # change the template used by ftw.table:
    table_template = None

    show_searchform = True
    depth = -1
    batching = ViewPageTemplateFile("batching.pt")
    template = ViewPageTemplateFile("generic.pt")
    select_all_template = ViewPageTemplateFile('select_all.pt')
    contents = []
    grouped = 0


    def __init__(self, context, request):
        super(ListingView, self).__init__(context, request)
        registry = getUtility(IRegistry)
        self.pagesize = \
            registry['ftw.tabbedview.interfaces.ITabbedView.batch_size']
        self.extjs_enabled = registry['ftw.tabbedview.interfaces.' + \
                                          'ITabbedView.extjs_enabled']

    def __call__(self, *args, **kwargs):
        # XXX : we need to be able to detect a extjs update request and return
        # only the template without data, because a later request will update
        # the table with json.
        # better approach to implement: create a new extjs-update-view witch
        # returns a json containing the template with data and the data as
        # json.

        if self.table_options is None:
            self.table_options = {}

        if self.extjs_enabled:
            if 'ext' in self.request:
                self.update()
                # add addition html that will be injected in the view
                static = {'static':{'batching': ''}}
                if not self.grouped:
                    static = {'static':{'batching': self.batching()}}
                self.table_options.update(static)
                return self.render_listing()
            else:
                self.contents = [{},]
                self.load_request_parameters()
                return self.template()

        self.update()
        return self.template()

    def load_request_parameters(self):
        """Load parameters such as page or filter from request.
        """

        # if the view is grouped batching will be disabled
        if len(self.request.get('groupBy', '')):
            self.grouped = 1

        if not self.grouped:
            # pagenumber
            self.batching_current_page = int(self.request.get('pagenumber', 1))
            # XXX eliminate self.pagenumber
            self.pagenumber = self.batching_current_page

            # pagesize
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
                           'DESC':'reverse'}.get(sort_order, sort_order)

        self.sort_reverse = self.sort_order == 'reverse'

    def update(self):
        self.load_request_parameters()
        # build the query
        query = self.table_source.build_query()

        # search
        results = self.table_source.search_results(query)
        results = self.custom_sort(results, self.sort_on, self.sort_reverse)
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
        if self.grouped:
            #if the view is grouped we disable batching
            rows = self.contents
        else:
            rows = self.batch
        return generator.generate(rows,
                                  self.columns,
                                  sortable = True,
                                  selected = (self.sort_on, self.sort_order),
                                  template = self.table_template,
                                  options = self.table_options,
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

    def select_all(self, pagenumber, selected_count):
        """Called when select-all is clicked. Returns HTML containing
        a hidden input field for each field which is not displayed at
        the moment.

        `pagenumber`: the current page number (1 is first page)
        `selected_count`: number of items selected / displayed on this page
        """

        if not self.batching_enabled:
            return

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
        return Batch(self.contents,
                     pagesize=self.pagesize,
                     pagenumber=self.pagenumber)

    @property
    def multiple_pages(self):
        """The multiple_pages in plone.app.batch has a bug
        if size == pagesize."""

        return len(self.contents) > self.pagesize


class CatalogListingView(ListingView, DefaultCatalogTableSourceConfig):

    # modify the base catalog query. This will be
    search_options = {}


    def update_config(self):
        DefaultCatalogTableSourceConfig.update_config(self)

        # configuration for the extjs grid
        extjs_conf = {'auto_expand_column':'sortable_title'}
        if self.extjs_enabled and isinstance(self.table_options, dict):
            self.table_options.update(extjs_conf)
        elif self.table_options is None:
            self.table_options = extjs_conf.copy()

        # search in current context by default
        self.filter_path = '/'.join(self.context.getPhysicalPath())
