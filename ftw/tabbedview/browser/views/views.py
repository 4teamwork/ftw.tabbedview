from Products.Five.browser import BrowserView
from ftw.table import helper
from Products.CMFCore.utils import getToolByName  
from zope.component import queryMultiAdapter  
from Products.CMFCore.Expression import getExprContext
from zope.component import queryUtility
from ftw.table.interfaces import ITableGenerator
from Products.ATContentTypes.interface import IATTopic
from zope.app.pagetemplate import ViewPageTemplateFile
from plone.app.content.batching import Batch
from plone.memoize import instance
from Acquisition import aq_inner

class TabbedView(BrowserView):
    
    def __init__(self, context, request): 
        super(TabbedView, self).__init__(context, request)
    
    def get_tabs(self):
        return self.get_actions(category='arbeitsraum-tabs') 
        #XXX use static tabs for development
        #return [{'id':'dossiers'}, {'id':'documents'}, ]

    def get_actions(self, category=''):
        types_tool = getToolByName(self.context, 'portal_types')
        ai_tool = getToolByName(self.context, 'portal_actionicons')
        actions = types_tool.listActions(object=self.context)   
        for action in actions:
            if action.category == category:
                icon = ai_tool.queryActionIcon(action_id=action.id, category=category, context=self.context)
                econtext = getExprContext(self.context, self.context)
                action = action.getAction(ec=econtext)
                if action['available'] and action['visible']:
                    view = self.context.restrictedTraverse("tabbedview_view-%s" % action['id'])
                    yield {
                           'id' : action['id'],
                           'icon' : icon,
                           'url' : action['url'],
                           'class' : ' '.join(view.get_css_classes()),
                           }
    
    def selected_tab(self):
        return 'Dokumente'

class BaseListingView(BrowserView):
    types = [] #friendly types
    #columns possible values
    # "<attributename>"
    # ('<attributename>', 'catalog_index')
    # ('<attributename>', callback)
    # ('<attributename>', '<catalog_index>', callback)
    # callback is used to modify the cell attribute E.g to humanize DateTime objects.
    # The Callback is called with the instance of the current item and the attributename
    columns = (('Title',), 
               ('modified',helper.readable_date), 
               ('Creator',helper.readable_author),)
               
    search_index = 'SearchableText'
    show_searchform = True
    sort_on = 'sortable_title'
    sort_order = 'reverse'
    search_options = {}
    
    depth = -1
    table = None
    batching = ViewPageTemplateFile("batching.pt")
        
    def __call__(self):      
        self.update()
        return super(BaseListingView, self).__call__()
        
    def get_css_classes(self):
        if self.show_searchform:
            return ['searchform-visible']
        else:
            return ['searchform-hidden']
        
    def render_listing(self):
        generator = queryUtility(ITableGenerator, 'ftw.tablegenerator') 
        return generator.generate(self.batch, 
                                  self.columns, 
                                  sortable=True, 
                                  selected=(self.sort_on, self.sort_order),
                                  template = self.table 
                                  )
 
    def update(self):
        catalog = getToolByName(self.context,'portal_catalog')
        self.pas_tool = getToolByName(self.context, 'acl_users')
        kwargs = {}
        
        self.pagesize = 20
        self.pagenumber =  int(self.request.get('pagenumber', 1))    
        self.url = self.context.absolute_url()
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
        
        if self.sort_on.startswith('header-'):
            kwargs['sort_on'] = self.sort_on = self.sort_on.split('header-')[1]
            
        kwargs['sort_order'] = self.sort_order = self.request.get('sort_order', self.sort_order)
        
        if IATTopic.providedBy(self.context):
            contentsMethod = self.context.queryCatalog
        else:
            contentsMethod = self.context.getFolderContents
        
        
        #overwrite options with search_options dict on tab
        kwargs.update(self.search_options)

        self.contents = catalog(path=dict(depth=self.depth, query='/'.join(self.context.getPhysicalPath())), **kwargs)
        #when we're searching recursively we have to remove the current item if its in self.types
        if self.depth != 1 and self.context.portal_type in self.types:
            index = 0
            current_path = '/'.join(self.context.getPhysicalPath())
            for result in self.contents:
                if current_path == result.getPath():
                    self.contents = list(self.contents)
                    self.contents.pop(index)
                    #removing from LazyMap doesn't work
                    #self.contents._len -= 1
                    #self.contents.actual_result_count -= 1
                    #res = self.contents._data.pop(index)
                index +=1
                
        self.len_results = len(self.contents)

    @property
    def buttons(self):
        buttons = []
        context = aq_inner(self.context)
        portal_actions = getToolByName(context, 'portal_actions')
        button_actions = portal_actions.listActionInfos(object=context, categories=('folder_buttons', ))
        # Do not show buttons if there is no data, unless there is data to be
        # pasted
        if not len(self.contents):
            if self.context.cb_dataValid():
                for button in button_actions:
                    if button['id'] == 'paste':
                        return [self.setbuttonclass(button)]
            else:
                return []

        for button in button_actions:
            # Make proper classes for our buttons
            if button['id'] != 'paste' or context.cb_dataValid():
                buttons.append(self.setbuttonclass(button)) 
        return buttons

    def setbuttonclass(self, button):
        if button['id'] == 'paste':
            button['cssclass'] = 'standalone'
        else:
            button['cssclass'] = 'context'
        return button

    @property
    @instance.memoize
    def batch(self):
        b = Batch(self.contents,pagesize=self.pagesize,pagenumber=self.pagenumber)
        return b
        
    def show_search_results(self):
        if self.request.has_key('searchable_text'):
            searchable_text = self.request.get('searchable_text')
            return bool(len(searchable_text))
        return False
        

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