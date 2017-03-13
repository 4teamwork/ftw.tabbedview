from ftw.tabbedview.testing import TABBEDVIEW_FUNCTIONAL_TESTING
from plone.app.caching.interfaces import IETagValue
from plone.app.testing import logout
from unittest2 import TestCase
from zope.component import getMultiAdapter


class TestETagValue(TestCase):
    layer = TABBEDVIEW_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def test_etag_value_returns_default_tab(self):
        tabbed_view = self.portal.unrestrictedTraverse('@@tabbed_view')
        self.assertEquals('', self.get_etag_value_for(tabbed_view))
        tabbed_view.set_default_tab('documents')
        self.assertEquals('documents', self.get_etag_value_for(tabbed_view))

    def test_default_value_is_empty_string(self):
        view = self.portal.unrestrictedTraverse('@@view')
        self.assertEquals('', self.get_etag_value_for(view))

    def test_default_value_is_empty_string_for_anonymous(self):
        logout()
        tabbed_view = self.portal.unrestrictedTraverse('@@tabbed_view')
        self.assertEquals('', self.get_etag_value_for(tabbed_view))

    def get_etag_value_for(self, view):
        adapter = getMultiAdapter((view, self.request),
                                  IETagValue,
                                  name='tabbedview')
        return adapter()
