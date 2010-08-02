from Products.Five.browser import BrowserView


class FallbackView(BrowserView):
    """ Fallback view if no view is registered for the tab """

    def view_name(self):
        """Returns the name of the view that must be implemented."""

        return 'tabbedview_view-%s' % self.request.get('view_name', '')
