from ftw.dictstorage.base import DictStorage
from ftw.dictstorage.interfaces import IConfig
from ftw.dictstorage.interfaces import IDictStorage
from ftw.tabbedview.interfaces import IDefaultDictStorageConfig
from ftw.tabbedview.interfaces import IGridStateStorageKeyGenerator
from persistent.dict import PersistentDict
from plone import api
from Products.CMFCore.utils import getToolByName
from zope.annotation import IAnnotations
from zope.component import adapts
from zope.interface import implements
from zope.publisher.interfaces.browser import IBrowserView


class DefaultGridStateStorageKeyGenerator(object):
    """Default implementation of the grid state storage key generator multi
    adapter. The default implementation uses following parts as key:
    * constant "ftw.tabbedview"
    * portal_type of context
    * name of the tab
    * username
    """

    implements(IGridStateStorageKeyGenerator)

    def __init__(self, context, tabview, request):
        self.context = context
        self.tabview = tabview
        self.request = request

    def get_key(self):
        if api.user.is_anonymous():
            return None

        key = []
        key.append('ftw.tabbedview')

        self._append_portal_type(key)
        self._append_view_name(key)
        self._append_userid(key)

        return '-'.join(key)

    def _append_view_name(self, key):
        key.append(self.tabview.__name__)

    def _append_portal_type(self, key):
        key.append(self.context.portal_type)

    def _append_userid(self, key):
        key.append(api.user.get_current().getId())


class DefaultDictStorageConfig(object):
    """Configures `ftw.dictstorage` to store its data as annotations on the
    plone site.
    """

    implements(IConfig, IDefaultDictStorageConfig)
    adapts(IBrowserView)

    def __init__(self, context):
        self.context = context

    def get_annotated_object(self):
        portal_url = getToolByName(self.context, 'portal_url')
        return portal_url.getPortalObject()

    def get_annotations_key(self):
        return 'ftw.dictstorage-data'


class DefaultDictStorage(DictStorage):
    implements(IDictStorage)
    adapts(IBrowserView, IDefaultDictStorageConfig)

    def __init__(self, context, config):
        self.context = context
        self.config = config

    @property
    def storage(self):
        obj = self.config.get_annotated_object()
        ann = IAnnotations(obj)

        key = self.config.get_annotations_key()
        if key not in ann.keys():
            ann[key] = PersistentDict()

        return ann[key]
