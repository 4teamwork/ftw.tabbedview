from AccessControl import getSecurityManager
from ftw.tabbedview.interfaces import IDefaultTabStorageKeyGenerator
from zope.component import adapts
from zope.interface import Interface
from zope.interface import implements
from zope.publisher.interfaces.browser import IBrowserView


class DefaultTabStorageKeyGenerator(object):
    """Generates the dictstorage key for storing the users default tab
    preference.
    """

    implements(IDefaultTabStorageKeyGenerator)
    adapts(Interface, IBrowserView, Interface)

    def __init__(self, context, view, request):
        self.context = context
        self.view = view
        self.request = request

    def get_key(self):
        user = getSecurityManager().getUser()
        parts = [
            'ftw.tabbedview',
            'defaulttab',
            self.context.portal_type,
            self.view.__name__,
            user.getId()]
        return '-'.join(parts)
