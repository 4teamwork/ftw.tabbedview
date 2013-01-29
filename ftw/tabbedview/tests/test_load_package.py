from Products.CMFCore.utils import getToolByName
from ftw.tabbedview.testing import TABBEDVIEW_INTEGRATION_TESTING
from unittest2 import TestCase


class TestWWWInstallation(TestCase):

    layer = TABBEDVIEW_INTEGRATION_TESTING

    def test_css_registered(self):
        portal = self.layer['portal']
        csstool = getToolByName(portal, 'portal_css')
        self.assertTrue(csstool.getResource(
                '++resource++ftw.tabbedview-resources/tabbedview.css'))
