from Products.CMFCore.utils import getToolByName
from zope.interface import implements
from ftw.tabbedview.interfaces import IGridStateStorageKeyGenerator


class DefaultGridStateStorageKeyGenerator(object):
    """Default implementation of the grid state storage key generator multi
    adapter. The default implementation uses following parts as key:
    * constant "ftw.tabbedview"
    * portal_type of context
    * name of the tab
    * username
    """

    implements(IGridStateStorageKeyGenerator)

    def __init__(self, context, tabview, request):
        self.context = context
        self.tabview = tabview
        self.request = request

    def get_key(self):
        key = []
        key.append('ftw.tabbedview')

        # add the portal_type of the context
        key.append(self.context.portal_type)

        # add the name of the tab
        key.append(self.tabview.__name__)

        # add the userid
        mtool = getToolByName(self.context, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        key.append(member.getId())

        # concatenate with "-"
        return '-'.join(key)
