from ftw.dictstorage.interfaces import IDictStorage
from ftw.tabbedview import tabbedviewMessageFactory as _
from ftw.tabbedview.interfaces import IDefaultTabStorageKeyGenerator
from ftw.tabbedview.interfaces import IGridStateStorageKeyGenerator
from ftw.tabbedview.interfaces import ITabbedViewEndpoints
from plone.registry.interfaces import IRegistry
from Products.CMFCore.Expression import getExprContext
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.i18n import translate
from zope.interface import implements
import AccessControl


try:
    from ftw.tabbedview.interfaces import ITabbedviewUploadable
except ImportError:
    QUICKUPLOAD_INSTALLED = False
else:
    QUICKUPLOAD_INSTALLED = True

try:
    import json
except ImportError:
    import simplejson as json


class TabbedView(BrowserView):
    """A View containing tabs with fancy ui"""

    implements(ITabbedViewEndpoints)

    __call__ = ViewPageTemplateFile("tabbed.pt")

    @property
    def macros(self):
        return self.__call__.macros

    def _resolve_tab(self, name):
        """Resolve the view responsible for a single tab.

        The views always must follow the naming-convention
        tabbedview_view-[name].

        """
        return self.context.restrictedTraverse(
            "@@tabbedview_view-{}".format(name),
            default=None)

    def user_is_logged_in(self):
        user = AccessControl.getSecurityManager().getUser()
        return user != AccessControl.SpecialUsers.nobody

    def get_tabs(self):
        """Returns a list of dicts containing the tabs definitions"""
        for action, icon in self.get_actions(category='tabbedview-tabs'):
            css_classes = None
            #get the css classes that should be set on the A elements.
            view = self._resolve_tab(action['id'])
            if not view:
                continue

            if hasattr(view, 'get_css_classes'):
                css_classes = ' '.join(view.get_css_classes())

            yield {
                'id': action['id'].lower(),
                'icon': icon,
                'url': action['url'],
                'class': css_classes,
                }

    def get_tab_items(self):
        """Returns the tab items from get_tabs with additional information for
        use in the tabbed template.
        """

        if not self.user_is_logged_in():
            default_tab = ''

        else:
            key_generator = getMultiAdapter((self.context, self, self.request),
                                            IDefaultTabStorageKeyGenerator)
            key = key_generator.get_key()
            default_tab = IDictStorage(self).get(key, '')

        actions = []

        for action in self.get_tabs():
            action = action.copy()
            if action['id'].lower() == default_tab:
                action['class'] = '%s initial' % action['class']

            view = self._resolve_tab(action['id'])
            action['tab_menu_actions'] = self.get_tab_menu_actions(view)

            actions.append(action)

        return actions

    def get_tab_menu_actions(self, view):
        """Returns a list of actions for the tab ``view``.
        """

        actions = [
            {'label': _(u'Set tab as default'),
             'href': 'javascript:tabbedview.set_tab_as_default()',
             'description': _(
                    u'Make the current tab the default tab when opening this '
                    u'view. This is a personal setting and does not impact '
                    u'other users.')
             }]

        if getattr(view, 'update_tab_actions', None) is not None:
            actions = view.update_tab_actions(actions)

        return actions

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
            listing_view = self._resolve_tab(view_name)

            if listing_view is None:
                listing_view = self._resolve_tab('fallback')

            self.request.response.setHeader('X-Tabbedview-Response', True)
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

        if not self.user_is_logged_in():
            return

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

        listing_view = self._resolve_tab(view_name)
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

        self.tab = self._resolve_tab(self.request.get('view_name'))

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

            if not member or member == AccessControl.SpecialUsers.nobody:
                return False

            if member.checkPermission(
                'Add portal content', self.context):

                registry = getUtility(IRegistry)
                upload_addable = registry.get(
                    'ftw.tabbedview.interfaces.ITabbedView'
                    '.quickupload_addable_types')

                for fti in self.context.allowedContentTypes():
                    if fti.id in upload_addable:
                        return True

        return False

    def set_default_tab(self, tab=None, view=None):
        """Sets the default tab. The id of the tab is passed as
        argument or in the request payload as ``tab``.
        """

        user = AccessControl.getSecurityManager().getUser()
        if user == AccessControl.SpecialUsers.nobody:
            tab = None

        else:
            tab = tab or self.request.get('tab')

        if not tab:
            return json.dumps([
                    'error',
                    translate('Error', 'plone', context=self.request),
                    translate(_(u'error_set_default_tab',
                                u'Could not set default tab.'),
                              context=self.request)])

        tab_title = translate(tab, 'ftw.tabbedview', context=self.request)
        success = [
            'info',
            translate('Information', 'plone', context=self.request),
            translate(_(u'info_set_default_tab',
                        u'The tab ${title} is now your default tab. ' +
                        u'This is a personal setting.',
                        mapping={'title': tab_title}),
                      context=self.request)]

        if not view and self.request.get('viewname', False):
            view = self.context.restrictedTraverse(
                self.request.get('viewname'))
        else:
            view = self

        key_generator = getMultiAdapter((self.context, view, self.request),
                                        IDefaultTabStorageKeyGenerator)
        key = key_generator.get_key()

        storage = IDictStorage(self)
        storage.set(key, tab.lower())

        return json.dumps(success)

    def msg_unknownresponse(self):
        """Return the message that is rendered when a javascript request gets
        a response from a different source than a tabbed view.

        This happens when a redirect occurs, for example a redirect to a login
        form due to a session timeout.
        """
        return _('There was an error loading the tab. Try '
                 '${anchor_open}reloading${anchor_close} the page.',
                 mapping={'anchor_open': '<a href="#" onclick="window.location.reload();">',
                          'anchor_close': '</a>'})
