from ftw.tabbedview.testing import TABBEDVIEW_FUNCTIONAL_TESTING
from ftw.testbrowser import browsing
from unittest import TestCase


class TestFallBackView(TestCase):

    layer = TABBEDVIEW_FUNCTIONAL_TESTING

    @browsing
    def test_fallback_view_is_registered(self, browser):
        browser.login().open(view='tabbedview_view-fallback',
                             data={'view_name': 'foo'})
        self.assertEqual(
            'No view registered for: tabbedview_view-foo',
            browser.css('body').first.text)

    @browsing
    def test_fallback_view_name_is_not_rendered_as_html(self, browser):
        browser.login().open(view='tabbedview_view-fallback',
                             data={'view_name': '<b>foo</b>'})
        self.assertEqual(
            'No view registered for: tabbedview_view-&lt;b&gt;foo&lt;/b&gt;',
            browser.css('body p').first.normalized_innerHTML)
