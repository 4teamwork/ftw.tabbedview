from Products.CMFCore.Expression import getExprContext
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from zope.component import queryMultiAdapter
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class TabbedView(BrowserView):

    template = ViewPageTemplateFile("tabbed.pt")
    
    def __call__(self):
        return self.template()
        
    def get_tabs(self):
        return self.get_actions(category='tabbedview-tabs')

    def get_actions(self, category=''):
        context = self.context
        types_tool = getToolByName(context, 'portal_types')
        ai_tool = getToolByName(context, 'portal_actionicons')
        actions = types_tool.listActions(object=context)
        for action in actions:
            if action.category == category:
                icon = ai_tool.queryActionIcon(action_id=action.id,
                                                category=category,
                                                context=context)
                econtext = getExprContext(context, context)
                action = action.getAction(ec=econtext)
                if action['available'] and action['visible']:
                    view_name = "tabbedview_view-%s" % action['id']
                    view = context.restrictedTraverse(view_name)
                    yield {
                        'id': action['id'].lower(),
                        'icon': icon,
                        'url': action['url'],
                        'class': ' '.join(view.get_css_classes()),
                        }
                        
    def listing(self):
        """Renders a listing"""
        view_name = self.request.get('view_name', None)
        if view_name:
            listing_view = queryMultiAdapter((self.context, self.request), 
                            name='tabbedview_view-%s' % view_name)
            if listing_view is None:
                listing_view = queryMultiAdapter((self.context, self.request), 
                                name='tabbedview_view-fallback')
            return listing_view()
            
    def select_all(self):
        """TODO: reimplement functionality copied from views.SelectAllView"""
        pass
        # self.tab = self.context.restrictedTraverse("tabbedview_view-%s" % self.request.get('view_name'))
        # self.tab.update()
        # 
        # return super(SelectAllView, self).__call__()
