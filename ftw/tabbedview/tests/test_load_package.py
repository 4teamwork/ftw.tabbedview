from Products.CMFCore.utils import getToolByName
from ftw.tabbedview.browser.tabbed import TabbedView
from ftw.tabbedview.testing import TABBEDVIEW_INTEGRATION_TESTING
from pyquery import PyQuery as pq
from unittest2 import TestCase
from zope.component import queryMultiAdapter


class FoobarView(TabbedView):
    def get_tabs(self):
        return [{'id': 'footab',
                 'class': None,
                 'title': 'MyTitle'}
        ]


class TestWWWInstallation(TestCase):

    layer = TABBEDVIEW_INTEGRATION_TESTING

    def test_css_registered(self):
        portal = self.layer['portal']
        csstool = getToolByName(portal, 'portal_css')
        self.assertTrue(csstool.getResource(
                '++resource++ftw.tabbedview-resources/tabbedview.css'))

    def test_tab_titles(self):
        portal = self.layer['portal']
        foobar_view = queryMultiAdapter((portal, portal.REQUEST),
                                        name='tabbed_view')
        html = foobar_view()
        doc = pq(html)
        tabs_html = doc('#tabbedview-header .tabbedview-tabs')
        self.assertGreater(len(tabs_html('#tab-footab')), 0)
        self.assertIn('MyTitle', tabs_html.html())
