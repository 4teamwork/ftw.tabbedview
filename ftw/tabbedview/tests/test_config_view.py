from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SpecialUsers import nobody
from AccessControl.SpecialUsers import system
from ftw.tabbedview.interfaces import ITabbedView
from ftw.tabbedview.testing import ZCML_LAYER
from ftw.testing import MockTestCase
from zope.component import provideUtility
from zope.component import queryMultiAdapter
import plone.registry


class TestTabbedviewConfigView(MockTestCase):

    layer = ZCML_LAYER

    def setUp(self):
        super(TestTabbedviewConfigView, self).setUp()

        self.registry = plone.registry.Registry()
        self.registry.registerInterface(ITabbedView)
        provideUtility(self.registry, plone.registry.interfaces.IRegistry)

        self.context = self.stub()
        self.request = self.stub_request()
        self.expect(self.request.get('PUBLISHED', None)).result(None)

    def tearDown(self):
        super(TestTabbedviewConfigView, self).tearDown()
        newSecurityManager(None, nobody)

    def test_component_registered(self):
        self.replay()

        view = queryMultiAdapter((self.context, self.request),
                                 name='tabbedview_config')
        self.assertNotEqual(view, None)

    def test_extjs_disabled_by_default(self):
        self.replay()

        view = queryMultiAdapter((self.context, self.request),
                                 name='tabbedview_config')
        self.assertEqual(view.extjs_enabled(), False)

    def test_extjs_enabled(self):
        key = 'ftw.tabbedview.interfaces.ITabbedView.extjs_enabled'
        self.registry[key] = True

        self.replay()

        newSecurityManager(None, system)
        view = queryMultiAdapter((self.context, self.request),
                                 name='tabbedview_config')
        self.assertEqual(view.extjs_enabled(), True)

    def test_extjs_anonymous_disabled(self):
        key = 'ftw.tabbedview.interfaces.ITabbedView.extjs_enabled'
        self.registry[key] = True

        self.replay()

        newSecurityManager(None, nobody)
        view = queryMultiAdapter((self.context, self.request),
                                 name='tabbedview_config')
        self.assertEqual(view.extjs_enabled(), False)
