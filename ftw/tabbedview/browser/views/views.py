from datetime import datetime, timedelta
import time
from Products.Five.browser import BrowserView
from ftw.table import helper
from Products.CMFCore.utils import getToolByName  
from zope.component import getMultiAdapter, queryMultiAdapter  
from zope.component import queryUtility
from plone.app.content.browser.folderfactories import _allowedTypes
from Products.statusmessages.interfaces import IStatusMessage
from zope.component import queryUtility
from ftw.table.interfaces import ITableGenerator
from Products.ATContentTypes.interface import IATTopic


class TabbedView(BrowserView):
    
    def __init__(self, context, request): 
        super(TabbedView, self).__init__(context, request)
    
    def get_tabs(self):
        #XXX use static tabs for development
        #return self.get_actions(category='arbeitsraum-tabs') 
        return [{'id':'dossiers'}, {'id':'documents'}, ]

    def get_actions(self, category=''):
        types_tool = getToolByName(self.context, 'portal_types')
        ai_tool = getToolByName(self.context, 'portal_actionicons')
        actions = types_tool.listActions(object=self.context)   
        for action in actions:
            if action.category == category:
                icon = ai_tool.queryActionIcon(action_id=action.id, category=category, context=self.context)
                econtext = getExprContext(self.context, self.context)
                action = action.getAction(ec=econtext)

                yield {
                       'id':action['id'],
                       'icon':icon,
                       'url':action['url']
                       }
    
    def selected_tab(self):
        return 'Dokumente'

class BaseListingView(BrowserView):
    types = [] #friendly types
    #columns possible values
    # "" = Name of index
    # ('','') = Title, index
    # ('','','') = title, index, method/attribute name
    # ('','', method) = title, index, callback 
    columns = (('Title',), 
               ('modified',helper.readable_date), 
               ('Creator',helper.readable_author),)
               
    columns_links = ['Title']
    search_index = 'SearchableText'
    sort_on = 'sortable_title'
    sort_order = 'reverse'
    
    
    def __call__(self):      
        self.search()
        return super(BaseListingView, self).__call__()
        
    def render_listing(self):
        generator = queryUtility(ITableGenerator, 'ftw.tablegenerator')
        return generator.generate(self.contents, self.columns)
 
    def search(self):
        catalog = getToolByName(self.context,'portal_catalog')
        self.pas_tool = getToolByName(self.context, 'acl_users')
        kwargs = {}
         
        if len(self.types):
            kwargs['portal_type'] = self.types
        else:
            kwargs['portal_type'] = self.context.getFriendlyTypes()
            
        if self.request.has_key('searchable_text'):
            searchable_text = self.request.get('searchable_text')
            if len(searchable_text):
                searchable_text = searchable_text.endswith('*') and searchable_text or searchable_text+'*'
                kwargs['SearchableText'] = searchable_text
        
        kwargs['sort_on'] = self.sort_on = self.request.get('sort_on', self.sort_on)
        kwargs['sort_order'] = self.sort_order = self.request.get('sort_order', self.sort_order)
        
        if IATTopic.providedBy(self.context):
            contentsMethod = self.context.queryCatalog
        else:
            contentsMethod = self.context.getFolderContents
        
        self.contents = results = catalog(path=dict(depth=1, query='/'.join(self.context.getPhysicalPath())), **kwargs)
        
    def show_search_results(self):
        if self.request.has_key('searchable_text'):
            searchable_text = self.request.get('searchable_text')
            return bool(len(searchable_text))
        return False
        
    def generate_class(self, index):
        class_ = 'sortable '
        if self.sort_on == index:
             class_ += 'sort-selected sort-%s'%self.sort_order
        return class_  

class GenericListing(BaseListingView):
    """ uses the tab id for self.types. Good for testing or fallback  """
    def __init__(self, context, request):
        """ kinda ugly way to get things done before GenericListing.__init__"""
        super(BaseListingView, self).__init__(context, request)
        ploneUtils = getToolByName(context, 'plone_utils')
        friendly_types = ploneUtils.getUserFriendlyTypes()     
        view_name = self.request.get('view_name', '')
        type_name = view_name.capitalize()
        if type_name in friendly_types:
            self.types = [type_name, ]
        
        super(GenericListing, self).__init__(context, request) 
    
class FallbackView(BrowserView):
    """ Default Fallback view if no view is registered for the tab """
    def __init__(self, context, request):      
        super(FallbackView, self).__init__(context, request)
        self.view_name = 'tabbedview_view-%s' % self.request.get('view_name', '')
    
class ChangeView(BrowserView):
    """Returns the content for the selected tab. """
    def __call__(self, view_name=""): 
        if view_name:
            self.body_view = queryMultiAdapter((self.context, self.request), name='tabbedview_view-%s' % view_name)  
            if self.body_view is None:
                self.body_view = queryMultiAdapter((self.context, self.request), name='tabbedview_view-fallback')         
            return super(BrowserView, self).__call__(self.context, self.request)          