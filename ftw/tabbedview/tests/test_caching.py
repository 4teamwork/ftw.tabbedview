from ftw.builder import Builder
from ftw.builder import create
from ftw.tabbedview.testing import TABBEDVIEW_FUNCTIONAL_TESTING
from plone.app.caching.interfaces import IETagValue
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from unittest import TestCase
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
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)
        folder = create(Builder("folder"))
        view = folder.unrestrictedTraverse('@@view')
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
