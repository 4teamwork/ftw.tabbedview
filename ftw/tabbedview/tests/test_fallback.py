from ftw.tabbedview.testing import ZCML_LAYER
from ftw.testing import MockTestCase
from zope.component import queryMultiAdapter, getMultiAdapter
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class TestFallBackView(MockTestCase):

    layer = ZCML_LAYER

    def test_component_registered(self):
        context = self.stub()
        request = self.providing_stub(IDefaultBrowserLayer)

        self.replay()

        view = queryMultiAdapter((context, request),
                                 name='tabbedview_view-fallback')
        self.assertNotEqual(view, None)

    def test_render_view(self):
        context = self.create_dummy()
        request = self.providing_stub(IDefaultBrowserLayer)
        request = self.stub_request()

        self.expect(request.get('view_name', '')).result('foo')

        self.replay()

        view = getMultiAdapter((context, request),
                               name='tabbedview_view-fallback')
        html = view()
        self.assertIn('No view registered for', html)
        self.assertIn('foo', html)
