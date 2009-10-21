"""Common configuration constants
"""

PROJECTNAME = 'ftw.tabbedview'

ADD_PERMISSIONS = {
    # -*- extra stuff goes here -*-
    'Arbeitsraum': 'ftw.tabbedview: Add Arbeitsraum',
}

INDEXES = (("getMeeting_type", "KeywordIndex"),
           ("sortable_creator", "KeywordIndex"),
           ("sortable_responsibility", "KeywordIndex"),
           ("getContentType", "KeywordIndex"),
          )
          
METADATA = ()