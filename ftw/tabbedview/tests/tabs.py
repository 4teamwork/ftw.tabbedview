from ftw.tabbedview.browser.listing import ListingView


class PublicTab(ListingView):
    pass


class SomeOtherTab(ListingView):

    def get_css_classes(self):
        return 'something'


class RestrictedTab(ListingView):
    pass
