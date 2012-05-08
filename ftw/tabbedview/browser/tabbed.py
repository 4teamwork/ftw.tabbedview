from Products.CMFCore.Expression import getExprContext
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ftw.dictstorage.interfaces import IDictStorage
from ftw.tabbedview.interfaces import IGridStateStorageKeyGenerator
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.component import queryMultiAdapter


try:
    from ftw.tabbedview.interfaces import ITabbedviewUploadable
except ImportError:
    QUICKUPLOAD_INSTALLED = False
else:
    QUICKUPLOAD_INSTALLED = True


class TabbedView(BrowserView):
    """A View containing tabs with fancy ui"""

    __call__ = ViewPageTemplateFile("tabbed.pt")

    def get_tabs(self):
        """Returns a list of dicts containing the tabs definitions"""
        for action, icon in self.get_actions(category='tabbedview-tabs'):
            css_classes = None
            #get the css classes that should be set on the A elements.
            view_name = "tabbedview_view-%s" % action['id']
            view = queryMultiAdapter((self.context, self.request),
                                     name=view_name, default=None)

            if view and hasattr(view, 'get_css_classes'):
                css_classes = ' '.join(view.get_css_classes())

            yield {
                'id': action['id'].lower(),
                'icon': icon,
                'url': action['url'],
                'class': css_classes,
                }

    def get_actions(self, category=''):
        """Returns the available and visible types actions
        in the given category
        """
        context = self.context
        types_tool = getToolByName(context, 'portal_types')
        ai_tool = getToolByName(context, 'portal_actionicons')
        actions = types_tool.listActions(object=context)
        plone_state = queryMultiAdapter((self.context, self.request),
                                        name='plone_portal_state')
        member = plone_state.member()

        for action in actions:
            wrong_permission = False
            for permission in action.permissions:
                if not member.has_permission(permission, self.context):
                    wrong_permission = True
                    continue

            if wrong_permission:
                continue

            if action.category == category:
                icon = ai_tool.queryActionIcon(action_id=action.id,
                                                category=category,
                                                context=context)
                econtext = getExprContext(context, context)
                action = action.getAction(ec=econtext)

                if action['available'] and action['visible']:
                    yield action, icon

    def listing(self):
        """Fetches the corresponding view which renders a listing.
        Called from javascript tabbedview.js in reload_view line 58
        """
        view_name = self.request.get('view_name', None)
        if view_name:
            listing_view = queryMultiAdapter((self.context, self.request),
                            name='tabbedview_view-%s' % view_name)

            if listing_view is None:
                listing_view = queryMultiAdapter(
                    (self.context, self.request),
                    name='tabbedview_view-fallback')

            return listing_view()

    def reorder(self):
        """Called when the items in the grid are reordered"""

        #ordered list of ids in the current tab
        positions = self.request.get('new_order[]')
        #orderd list of allids within the container
        object_ids = self.context.objectIds(ordered=True)
        #move and order tab content in the desired order before
        #the remaining objects
        state = self.context.moveObjectsByDelta(positions, -len(object_ids))
        return str(state)

    def setgridstate(self):
        """Stores the current grid configuration (visible columns,
        column order, grouping, sorting etc.) persistent in dictstorage.
        """

        # extract the data
        state = self.request.get('gridstate', None)
        if not state or not isinstance(state, str):
            return

        if state == '{}':
            state = ''

        # get the tab view
        view_name = self.request.get('view_name', None)
        if not view_name:
            return

        listing_view = queryMultiAdapter((self.context, self.request),
                            name='tabbedview_view-%s' % view_name)
        if not listing_view:
            return

        # get the key for storing the state
        generator = queryMultiAdapter(
            (self.context, listing_view, self.request),
            IGridStateStorageKeyGenerator)
        key = generator.get_key()

        # store the data
        storage = IDictStorage(listing_view)
        storage.set(key, state)

    def select_all(self):
        """Called when select-all is clicked. Returns HTML containing
        a hidden input field for each field which is not displayed at
        the moment.
        """

        self.tab = self.context.restrictedTraverse("tabbedview_view-%s" %
                                          self.request.get('view_name'))

        return self.tab.select_all(
            int(self.request.get('pagenumber', 1)),
            int(self.request.get('selected_count', 0)))

    def show_uploadbox(self):
        """check if the uploadbox is activated for the current context"""

        if not QUICKUPLOAD_INSTALLED:
            return False

        if ITabbedviewUploadable.providedBy(self.context):
            member = getToolByName(
                self.context, 'portal_membership').getAuthenticatedMember()
            if member.checkPermission(
                'Add portal content', self.context):

                registry = getUtility(IRegistry)
                upload_addable = registry.get(
                    'ftw.tabbedview.interfaces.ITabbedView' + \
                        '.quickupload_addable_types')

                for fti in self.context.allowedContentTypes():
                    if fti.id in upload_addable:
                        return True

        return False
