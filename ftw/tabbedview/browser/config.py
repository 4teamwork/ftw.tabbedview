from Products.Five.browser import BrowserView
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
import AccessControl
from ftw.tabbedview.interfaces import INoExtJS

class TabbedviewConfigView(BrowserView):

    def extjs_enabled(self, view=None):
        """Returns `True` if extjs is enabled.
        """
        if view is None:
            view = self.request.get('PUBLISHED', None)

        if INoExtJS.providedBy(view):
            return False

        user = AccessControl.getSecurityManager().getUser()
        if user == AccessControl.SpecialUsers.nobody:
            # ExtJS is not supported for anonymous users, since we are not
            # able to store the state. Things such as sorting would not even
            # work in the session.
            return False

        registry = getUtility(IRegistry)
        return registry['ftw.tabbedview.interfaces.'
                        'ITabbedView.extjs_enabled']
