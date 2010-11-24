from zope import schema
from zope.interface import Interface


class ITabbedView(Interface):
    """A type for collaborative spaces."""

    batch_size = schema.Int(title=u"Batch Size", min=1, default=50)

    timeout = schema.Int(title=u"Timeout for ajax Requests in ms",
                         min=500, default=5000)

    extjs_enabled = schema.Bool(title=u'Extjs is enabled',
                                default=False)


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
