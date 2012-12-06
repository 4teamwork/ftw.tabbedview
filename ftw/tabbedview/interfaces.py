# pylint: disable=E0211, E0213
# E0211: Method has no argument
# E0213: Method should have "self" as first argument

from zope import schema
from zope.interface import Interface

try:
    from collective.quickupload.browser.interfaces import IQuickUploadCapable
except ImportError:
    QUICKUPLOAD_INSTALLED = False
else:
    QUICKUPLOAD_INSTALLED = True


class ITabbedView(Interface):
    """A type for collaborative spaces."""

    batch_size = schema.Int(title=u"Batch Size", min=1, default=50)

    timeout = schema.Int(title=u"Timeout for ajax Requests in ms",
                         min=500, default=5000)

    extjs_enabled = schema.Bool(title=u'Extjs is enabled',
                                default=False)

    dynamic_batchsize_enabled = schema.Bool(
        title=u'Display the Batch size input field.',
        default=False)

    max_dynamic_batchsize = schema.Int(
        title=u'Dynamic batchsize maximum',
        default=500,)

    quickupload_addable_types = schema.List(
        title=u'',
        description=u'Types which are addable with quickupload',
        default=["File", ],
        value_type=schema.TextLine(),
        )


class IListingView(Interface):
    """Marker interface for listing tabs.
    """

    def update_tab_actions(actions):
        """Allows to change the default actions for a tab. The ``actions``
        argument contains a list of actions (dicts) and should be returned by
        this method after modifying it.

        Example actions:
        [{'label': _(u'Reset table configuration'),
          'href': 'javascript:reset_grid_state()',
          'description': _(u'Resets the table configuration for this tab.'),
          'class': 'additional-css-class'}]
        """


class IGridStateStorageKeyGenerator(Interface):
    """Adapter interface for a multi adapter which provides a key for storing
    the grid state in dictstorage with. Dependending on the key the same state
    is stored for more or less tabs (shared).
    """

    def __init__(context, tabview, request):
        """The multi-adapter adapts (context, tabview, request).
        """

    def get_key():
        """Returns a string which is used for storing the state in the
        dictstorage.
        """


class IDefaultTabStorageKeyGenerator(Interface):
    """Generates the dictstorage key for storing the users default tab
    preference.
    """

    def __init__(context, view, request):
        """Adapter arguments:
        - context: the current context
        - view: the tabbed-view (not the tab)
        - request: the request.
        """

    def get_key():
        """Returns the key for the dictstorage where the default tab is
        stored.
        """


class IDefaultDictStorageConfig(Interface):
    """The default dict storage configuration configures `ftw.dictstorage`
    to store its data as annotations on the plone site root.
    """

    def get_annotated_object():
        """Returns the annotated object (the plone site by default).
        """


class IExtFilter(Interface):
    """An ExtJS column filter definition.
    When defining columns (in dict-syntax), define an object providing
    IExtFilter as 'filter'.
    """

    def get_default_value(column):
        """Returns the the default filter value. If None is returned, this
        column is not filtered by default.
        """

    def get_filter_definition(column, contents):
        """Arguments:

        *column* the original column definition dict, usable for generic
        filters which need to know the column id.
        *contents* the search results (e.g. set of brain)

        Returns an ExtJS filter definition dict with keys:

        *type* - the filter type (e.g. string, list, boolean, numeric, date)
        *options* -- if the filter type is list this should be a list of all
        possible values as tuples with key / label. (optional)
        *comparison* -- if the filter type is date, put the comparison
        operator here (ne, eq, gt, lt). (optional)
        """

    def apply_filter_to_query(column, query, data):
        """If the filter is active, extend the query so that it filters the
        passed values.

        Arguments:
        *column* - the column definition
        *query* - the query to be modified and returned
        *data* - a dict of filter data, containing usually the key ``value``
        with the filter value but may also contain additional information
        such as an ``operator`` for date filters. When using a default
        filter, this dict only contains the value.

        Warning: get_filter_definition will be called afterwards and will
        contain the already filtered result set.
        """

if QUICKUPLOAD_INSTALLED:
    class ITabbedviewUploadable(Interface, IQuickUploadCapable):
        """Marker interfaces"""
