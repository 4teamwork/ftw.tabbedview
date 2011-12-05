from plone.app.layout.viewlets import common
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ftw.tabbedview.browser.tabbed import TabbedView


class SearchBox(common.ViewletBase):
    index = ViewPageTemplateFile('searchbox.pt')

    def available(self):
        try:
            view = self.context.restrictedTraverse(
                self.view.__name__.encode('utf-8'))
        except AttributeError:
            return False
        return isinstance(view, TabbedView)

    def render(self):
        if not self.available():
            return ''
        else:
            return common.ViewletBase.render(self)
