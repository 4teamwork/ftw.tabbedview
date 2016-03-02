from ftw.tabbedview.testing import TABBEDVIEW_FUNCTIONAL_TESTING
from ftw.testbrowser import browsing
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from unittest2 import TestCase
import transaction


class TestTabPermissions(TestCase):

    layer = TABBEDVIEW_FUNCTIONAL_TESTING

    @browsing
    def test_restricted_tabs_invisible_with_unprivileded_user(self, browser):
        browser.login().visit(view='tabbed_view')
        self.assertEqual(['MyTitle', 'notranslation'],
                         browser.css('.tabbedview-tabs .formTab').text)

    @browsing
    def test_restricted_tabs_visible_with_privileded_user(self, browser):
        setRoles(self.layer['portal'], TEST_USER_ID, ['Member', 'Editor'])
        transaction.commit()

        browser.login().visit(view='tabbed_view')
        self.assertEqual(['MyTitle', 'notranslation', 'Restricted Tab'],
                         browser.css('.tabbedview-tabs .formTab').text)

    def test_get_tabs(self):
        view = self.layer['portal'].restrictedTraverse('tabbed_view')

        self.assertEqual([
            {'url': '#',
             'class': 'searchform-visible',
             'id': 'footab',
             'icon': None},
            {'url': '#',
             'class': 'searchform-visible',
             'id': 'notranslation',
             'icon': None}],
            list(view.get_tabs()))
