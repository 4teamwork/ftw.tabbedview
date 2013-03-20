from unittest2 import TestCase
from ftw.tabbedview.browser.listing import batch_method
from pkg_resources import get_distribution


class TestBatchImport(TestCase):

    def test_import(self):
        if get_distribution('Products.CMFPlone').version.startswith('4.3'):
            # plone.batching
            self.assertEquals(batch_method.__name__, 'fromPagenumber')
        else:
            # plone.app.content.batching
            self.assertEquals(batch_method.__name__, 'Batch')
