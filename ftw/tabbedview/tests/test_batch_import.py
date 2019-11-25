from unittest import TestCase
from ftw.tabbedview.browser.listing import batch_method
from pkg_resources import get_distribution


class TestBatchImport(TestCase):

    def test_import(self):
        if float(get_distribution('Products.CMFPlone').version[:3]) >= 4.3:
            # plone.batching
            self.assertEquals(batch_method.__name__, 'fromPagenumber')
        else:
            # plone.app.content.batching
            self.assertEquals(batch_method.__name__, 'Batch')
