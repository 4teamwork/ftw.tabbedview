from Products.Five.browser import BrowserView
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
import AccessControl


class TabbedviewConfigView(BrowserView):

    def extjs_enabled(self):
        """Returns `True` if extjs is enabled.
        """

        user = AccessControl.getSecurityManager().getUser()
        if user == AccessControl.SpecialUsers.nobody:
            # ExtJS is not supported for anonymous users, since we are not
            # able to store the state. Things such as sorting would not even
            # work in the session.
            return False

        registry = getUtility(IRegistry)
        return registry['ftw.tabbedview.interfaces.'
                        'ITabbedView.extjs_enabled']
