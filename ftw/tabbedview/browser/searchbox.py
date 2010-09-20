from plone.app.layout.viewlets import common
from zope.component import getMultiAdapter
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ftw.tabbedview.browser.tabbed import TabbedView


class SearchBox(common.ViewletBase):
    index = ViewPageTemplateFile('searchbox.pt')

    def available(self):
        plone = getMultiAdapter((self.context, self.request),
                                name=u'plone_context_state')
        try:
            view = self.context.restrictedTraverse(plone.view_template_id())
        except AttributeError:
            return False
        return isinstance(view, TabbedView)

    def render(self):
        if not self.available():
            return ''
        else:
            return common.ViewletBase.render(self)
