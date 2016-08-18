# pylint: disable=E0211, E0213
# E0211: Method has no argument
# E0213: Method should have "self" as first argument

from zope import schema
from zope.interface import Interface

try:
    from collective.quickupload.interfaces import IQuickUploadCapable
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


class ITabbedViewEndpoints(Interface):

    def listing():
        """Fetches the corresponding view which renders a listing.
        Called from javascript tabbedview.js in reload_view.
        """

    def select_all():
        """Called when select-all is clicked. Returns HTML containing
        a hidden input field for each field which is not displayed at
        the moment.
        """

    def reorder():
        """Called when the items in the grid are reordered"""

    def setgridstate():
        """Stores the current grid configuration (visible columns,
        column order, grouping, sorting etc.) persistent in dictstorage.
        """

    def set_default_tab(tab=None, view=None):
        """Sets the default tab. The id of the tab is passed as
        argument or in the request payload as ``tab``.
        """

    def msg_unknownresponse():
        """Return the message that is rendered when a javascript request gets
        a response from a different source than a tabbed view.

        This happens when a redirect occurs, for example a redirect to a login
        form due to a session timeout.
        """


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


class INoExtJS(Interface):
    """Marker interface for tabbedviews to force disable extjs"""


if QUICKUPLOAD_INSTALLED:
    class ITabbedviewUploadable(Interface, IQuickUploadCapable):
        """Marker interfaces"""
