from ftw.dictstorage.interfaces import IDictStorage
from ftw.tabbedview.interfaces import IDefaultTabStorageKeyGenerator
from ftw.tabbedview.testing import TABBEDVIEW_INTEGRATION_TESTING
from Products.CMFCore.utils import getToolByName
from pyquery import PyQuery as pq
from unittest2 import TestCase
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter


class TestWWWInstallation(TestCase):

    layer = TABBEDVIEW_INTEGRATION_TESTING

    def test_css_registered(self):
        portal = self.layer['portal']
        csstool = getToolByName(portal, 'portal_css')
        self.assertTrue(csstool.getResource(
            '++resource++ftw.tabbedview-resources/tabbedview.css'))

    def test_initial_tab_is_reseted_on_every_request(self):
        portal = self.layer['portal']
        foobar_view = queryMultiAdapter((portal, portal.REQUEST),
                                        name='tabbed_view')
        key_generator = getMultiAdapter((portal, foobar_view, portal.REQUEST),
                                        IDefaultTabStorageKeyGenerator)
        key = key_generator.get_key()

        # first call
        IDictStorage(foobar_view)[key] = 'footab'
        html = foobar_view()
        doc = pq(html)
        initial_tab = doc('#tabbedview-header .tabbedview-tabs a.initial')
        self.assertEqual(1, len(initial_tab))
        self.assertEqual('MyTitle', initial_tab.text())

        # second call
        IDictStorage(foobar_view)[key] = 'notranslation'
        html = foobar_view()
        doc = pq(html)
        initial_tab = doc('#tabbedview-header .tabbedview-tabs a.initial')
        self.assertEqual(1, len(initial_tab))
        self.assertEqual('notranslation', initial_tab.text())
