from Products.Five.browser import BrowserView


class FallbackView(BrowserView):
    """ Fallback view if no view is registered for the tab """

    def __init__(self, context, request):
        super(FallbackView, self).__init__(context, request)
        self.view_name = ('tabbedview_view-%s' % 
                            self.request.get('view_name', ''))