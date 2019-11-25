from ftw.dictstorage.interfaces import IConfig
from mock import Mock
from ftw.dictstorage.interfaces import IDictStorage
from ftw.tabbedview import statestorage
from ftw.tabbedview.interfaces import IDefaultDictStorageConfig
from ftw.tabbedview.interfaces import IGridStateStorageKeyGenerator
from ftw.tabbedview.testing import TABBEDVIEW_FUNCTIONAL_TESTING
from ftw.tabbedview.testing import ZCML_LAYER
from ftw.testing import MockTestCase
from persistent.mapping import PersistentMapping
from unittest import TestCase
from zope.annotation import IAttributeAnnotatable
from zope.component import getAdapter
from zope.component import getMultiAdapter
from zope.interface.verify import verifyClass
from zope.publisher.interfaces.browser import IBrowserView


class TestDefaultGridStateStorageKeyGenerator(TestCase):

    layer = TABBEDVIEW_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestDefaultGridStateStorageKeyGenerator, self).setUp()
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def test_component_registered(self):
        view = getMultiAdapter((self.portal, self.request), name='tabbed_view')
        component = getMultiAdapter((self.portal, view, self.request),
                                    IGridStateStorageKeyGenerator)

        self.assertEqual(type(component),
                         statestorage.DefaultGridStateStorageKeyGenerator)

    def test_implements_interface(self):
        self.assertTrue(IGridStateStorageKeyGenerator.implementedBy(
            statestorage.DefaultGridStateStorageKeyGenerator))

        verifyClass(IGridStateStorageKeyGenerator,
                    statestorage.DefaultGridStateStorageKeyGenerator)

    def test_get_key(self):
        view = getMultiAdapter((self.portal, self.request), name='tabbed_view')
        component = getMultiAdapter((self.portal, view, self.request),
                                    IGridStateStorageKeyGenerator)

        self.assertEqual('ftw.tabbedview-Plone Site-tabbed_view-test_user_1_',
                         component.get_key())


class TestDefaultDictStorageConfig(MockTestCase):

    layer = ZCML_LAYER

    def test_component_registered(self):
        context = self.providing_stub(IBrowserView)
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

        portal_url = Mock()
        self.mock_tool(portal_url, 'portal_url')
        portal_url.getPortalObject.return_value = site

        context = self.providing_stub(IBrowserView)
        component = getAdapter(context, IConfig)
        self.assertEqual(component.get_annotated_object(), site)

    def test_get_annotations_key(self):
        context = self.providing_stub(IBrowserView)
        component = getAdapter(context, IConfig)
        self.assertEqual(component.get_annotations_key(),
                         'ftw.dictstorage-data')


class TestDefaultDictStorage(MockTestCase):

    layer = ZCML_LAYER

    def test_component_registered(self):
        context = self.providing_stub(IBrowserView)
        config = self.providing_stub(IDefaultDictStorageConfig)
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

        config.get_annotated_object.return_value = site
        config.get_annotations_key.return_value = 'ftw.dictstorage-data'
        component = getMultiAdapter((context, config), IDictStorage)

        self.assertEqual(type(component.storage), PersistentMapping)
