from zope import schema
from zope.interface import Interface

# -*- extra stuff goes here -*-

class ITabbedView(Interface):
    """A type for collaborative spaces."""
    
    batch_size = schema.Int(title=u"Batch Size", min=10, default=50)
    timeout = schema.Int(title=u"Timeout for ajax Requests in ms", min=500, default=5000)
    