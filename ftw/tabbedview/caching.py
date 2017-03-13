from ftw.dictstorage.interfaces import IDictStorage
from ftw.tabbedview.interfaces import IDefaultTabStorageKeyGenerator
from plone.app.caching.interfaces import IETagValue
from plone.app.caching.operations.utils import getContext
from zope.component import adapts
from zope.component import queryMultiAdapter
from zope.interface import implements
from zope.interface import Interface


class TabbedviewETagValue(object):
    implements(IETagValue)
    adapts(Interface, Interface)

    def __init__(self, published, request):
        self.published = published
        self.request = request

    def __call__(self):
        storage_key_generator = queryMultiAdapter(
            (getContext(self.published), self.published, self.request),
            IDefaultTabStorageKeyGenerator)
        if storage_key_generator is None:
            return ''

        storage_key = storage_key_generator.get_key()
        return IDictStorage(self.published).get(storage_key) or ''
