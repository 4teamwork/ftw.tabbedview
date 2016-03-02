from ftw.tabbedview.testing import TABBEDVIEW_FUNCTIONAL_TESTING
from ftw.testbrowser import browsing
from ftw.testing import MockTestCase


class TestFallBackView(MockTestCase):

    layer = TABBEDVIEW_FUNCTIONAL_TESTING

    @browsing
    def test_fallback_view_is_registered(self, browser):
        browser.login().open(view='tabbedview_view-fallback',
                             data={'view_name': 'foo'})
        self.assertEqual(
            'No view registered for: tabbedview_view-foo',
            browser.css('body').first.text)
