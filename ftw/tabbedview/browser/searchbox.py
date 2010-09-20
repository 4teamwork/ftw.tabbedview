from plone.app.layout.viewlets import common
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class SearchBox(common.ViewletBase):
    index = ViewPageTemplateFile('searchbox.pt')