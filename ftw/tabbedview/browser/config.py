from Products.Five.browser import BrowserView
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


class TabbedviewConfigView(BrowserView):

    def extjs_enabled(self):
        """Returns `True` if extjs is enabled.
        """
        registry = getUtility(IRegistry)
        return registry['ftw.tabbedview.interfaces.'
                        'ITabbedView.extjs_enabled']
