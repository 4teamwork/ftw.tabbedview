from OFS.interfaces import IItem
from ftw.dictstorage.interfaces import IConfig
from ftw.dictstorage.interfaces import IDictStorage
from ftw.tabbedview import statestorage
from ftw.tabbedview.interfaces import IDefaultDictStorageConfig
from ftw.tabbedview.interfaces import IGridStateStorageKeyGenerator
from ftw.tabbedview.testing import ZCML_LAYER
from ftw.testing import MockTestCase
from persistent.mapping import PersistentMapping
from zope.annotation import IAttributeAnnotatable
from zope.component import getAdapter
from zope.component import getMultiAdapter
from zope.interface.verify import verifyClass
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.browser import IBrowserView


class TestDefaultGridStateStorageKeyGenerator(MockTestCase):

    layer = ZCML_LAYER

    def test_component_registered(self):
        context = self.providing_stub(IItem)
        tabview = self.providing_stub(IBrowserView)
        request = self.providing_stub(IBrowserRequest)

        self.replay()

        component = getMultiAdapter((context, tabview, request),
                                    IGridStateStorageKeyGenerator)

        self.assertEqual(type(component),
                         statestorage.DefaultGridStateStorageKeyGenerator)

    def test_implements_interface(self):
        self.assertTrue(IGridStateStorageKeyGenerator.implementedBy(
                statestorage.DefaultGridStateStorageKeyGenerator))

        verifyClass(IGridStateStorageKeyGenerator,
                    statestorage.DefaultGridStateStorageKeyGenerator)

    def test_get_key(self):
        context = self.providing_stub(IItem)
        self.expect(context.portal_type).result('Document')
        tabview = self.providing_stub(IBrowserView)
        self.expect(tabview.__name__).result('documents')
        request = self.providing_stub(IBrowserRequest)

        mtool = self.stub()
        self.mock_tool(mtool, 'portal_membership')
        self.expect(mtool.getAuthenticatedMember().getId()).result('john.doe')

        self.replay()
        component = getMultiAdapter((context, tabview, request),
                                    IGridStateStorageKeyGenerator)

        self.assertEqual(component.get_key(),
                         'ftw.tabbedview-Document-documents-john.doe')


class TestDefaultDictStorageConfig(MockTestCase):

    layer = ZCML_LAYER

    def test_component_registered(self):
        context = self.providing_stub(IBrowserView)

        self.replay()
        component = getAdapter(context, IConfig)
        self.assertEqual(type(component),
                         statestorage.DefaultDictStorageConfig)

    def test_implements_interfaces(self):
        # IConfig interface
        self.assertTrue(IConfig.implementedBy(
                statestorage.DefaultDictStorageConfig))

        verifyClass(IConfig, statestorage.DefaultDictStorageConfig)

        # IDefaultDictStorageConfig
        self.assertTrue(IDefaultDictStorageConfig.implementedBy(
                statestorage.DefaultDictStorageConfig))

        verifyClass(IDefaultDictStorageConfig,
                    statestorage.DefaultDictStorageConfig)

    def test_get_annotated_object_is_plone_site(self):
        site = self.create_dummy()

        portal_url = self.mocker.mock()
        self.mock_tool(portal_url, 'portal_url')
        self.expect(portal_url.getPortalObject()).result(site)

        context = self.providing_stub(IBrowserView)

        self.replay()
        component = getAdapter(context, IConfig)
        self.assertEqual(component.get_annotated_object(), site)

    def test_get_annotations_key(self):
        context = self.providing_stub(IBrowserView)

        self.replay()
        component = getAdapter(context, IConfig)
        self.assertEqual(component.get_annotations_key(),
                         'ftw.dictstorage-data')


class TestDefaultDictStorage(MockTestCase):

    layer = ZCML_LAYER

    def test_component_registered(self):
        context = self.providing_stub(IBrowserView)
        config = self.providing_stub(IDefaultDictStorageConfig)

        self.replay()
        component = getMultiAdapter((context, config), IDictStorage)
        self.assertEqual(type(component), statestorage.DefaultDictStorage)

    def test_implements_interface(self):
        self.assertTrue(IDictStorage.implementedBy(
                statestorage.DefaultDictStorage))

        verifyClass(IDictStorage,
                    statestorage.DefaultDictStorage)

    def test_storage_is_persistent(self):
        site = self.providing_stub(IAttributeAnnotatable)
        context = self.providing_stub(IBrowserView)
        config = self.providing_stub(IDefaultDictStorageConfig)

        self.expect(config.get_annotated_object()).result(site)
        self.expect(config.get_annotations_key()).result(
            'ftw.dictstorage-data')

        self.replay()
        component = getMultiAdapter((context, config), IDictStorage)

        self.assertEqual(type(component.storage), PersistentMapping)
