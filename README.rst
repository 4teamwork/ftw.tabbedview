Introduction
============

This package provides a generic view with multiple tabs for plone. It
provides a generic base tab for listing contents in a table, based on
`ftw.table`_.


Features
========

- Generic tabbed view
- Tabs are registered through FTI actions
- Base view for listing tabs
- Listing tabs are filterable
- Perform configurable actions on listed items
- `ftw.table`_'s `Ext JS`_ support works also in listing tables
- Fallback tables
- Drag'n drop multiple file upload functionality (using quickupload plugin)


Installation
============


**Default table implementation**

- Add ``ftw.tabbedview`` to your buildout (or as dependency to a custom egg):

::

    [buildout]
    parts =
        instance
        ...

    [instance]
    ...
    eggs +=
        Plone
        ftw.tabbedview

- Install default profile in portal_setup.


**Ext JS table implementation**

- Add ``ftw.tabbedview`` to your buildout (or as dependency to a custom egg),
  using the ``extjs`` extras require:

::

    [buildout]
    parts =
        instance
        ...

    [instance]
    ...
    eggs +=
        Plone
        ftw.tabbedview[extjs]

- Install extjs profile in portal_setup.


Quickupload plugin implementation
---------------------------------

The quickupload plugin integrates the `collective.quickupload`_ packages in to the tabbedview.

- Add ``ftw.tabbedview`` to your buildout (or as dependency to a custom egg),
  using the ``quickupload`` extras require:

::

    [buildout]
    parts =
        instance
        ...

    [instance]
    ...
    eggs +=
        Plone
        ftw.tabbedview[quickupload]

- Install quickupload profile in portal_setup.

- For activating the quickupload plugin on a context, make sure the context provides the ITabbedviewUploadable Interface.

=====
Usage
=====

We use the package ``example.conference``_ as example for showing how to use ``ftw.tabbedview``.

- Use the ``@@tabbed_view`` on any container.

- Define actions on the content type FTI (Example: ``profiles/default/types/example.conference.program.xml``)::

    <?xml version="1.0"?>
    <object name="example.conference.program" meta_type="Dexterity FTI"
            i18n:domain="example.conference" xmlns:i18n="http://xml.zope.org/namespaces/i18n">

      <property name="default_view">tabbed_view</property>
      <property name="view_methods">
          <element value="tabbed_view"/>
      </property>

      <action title="Sessions" action_id="sessions" category="tabbedview-tabs"
              condition_expr="" url_expr="string:${object_url}?view=sessions"
              visible="True">
          <permission value="View"/>
      </action>

    </object>

- Create the "tab" view (Example: ``browser/tabs.py``)::

    >>> from ftw.tabbedview.browser.listing import CatalogListingView
    >>> from ftw.table import helper
    >>> from example.conference import _
    >>>
    >>> class SessionsTab(CatalogListingView):
    ...     """A tabbed-view tab listing sessions on a program.
    ...     """
    ...
    ...     types = ['example.conference.session']
    ...     sort_on = 'sortable_title'
    ...
    ...     show_selects = False
    ...
    ...     columns = (
    ...         {'column': 'Title',
    ...          'sort_index': 'sortable_title',
    ...          'column_title': _(u'Title'),
    ...          'helper': helper.linked},
    ...
    ...         {'column': 'Track',
    ...          'column_title': _(u"Track")},
    ...         )

- Register the view using ZCML, be sure to name it ``tabbedview_view-${action id}``
  (Example: ``browser/configure.zcml``)::

    <configure
        xmlns="http://namespaces.zope.org/zope"
        xmlns:browser="http://namespaces.zope.org/browser">

        <browser:page
            for="example.conference.program.IProgram"
            name="tabbedview_view-sessions"
            class=".tabs.SessionsTab"
            permission="zope2.View"
            />

    </configure>


Alternative listing sources
===========================

It is possible to use alternative sources for listing tabs. The tables are generated
using `ftw.table`_ and the tab is a ``ftw.table.interfaces.ITableSourceConfig``, which
allows ``ftw.table`` to find an appropriate source. Subclassing ``ITableSourceConfig`` and
registering a custom ``ITableSource`` multi adapter makes it possible to use alternative
data sources such as sqlalchemy or structured python data (local roles for instance).
Take a look at the `ftw.table`_ documentation for more details.


Screenshots
===========

Screenshot of a example tabbed view using the default table implementation:

.. image:: https://github.com/4teamwork/ftw.tabbedview/raw/master/docs/screenshot1.png

Screenshot of the same listing using the ``extjs`` table implementation:

.. image:: https://github.com/4teamwork/ftw.tabbedview/raw/master/docs/screenshot2.png


Caching
=======

``ftw.tabbedview`` provides a ``plone.app.caching`` etag adapter
named ``tabbedview``.
This etag can be used in the caching configuration in order to make the cache
flush when changing the default tab.

In order to enable this, you need to add it to your caching configuration.
Depending on how you want to set up caching in your project, you may want
to add the etag to your rulesets.
You can do that in a ``registry.xml``:

.. code:: xml

    <?xml version="1.0"?>
    <registry>

        <record name="plone.app.caching.weakCaching.plone.content.itemView.etags">
            <value purge="False">
                <element>tabbedview</element>
            </value>
        </record>

        <record name="plone.app.caching.weakCaching.plone.content.folderView.etags">
            <value purge="False">
                <element>tabbedview</element>
            </value>
        </record>

    </registry>


Links
=====

- Github: https://github.com/4teamwork/ftw.tabbedview
- Issues: https://github.com/4teamwork/ftw.tabbedview/issues
- Pypi: http://pypi.python.org/pypi/ftw.tabbedview
- Continuous integration: https://jenkins.4teamwork.ch/search?q=ftw.tabbedview



Licensing
=========

This package is released under GPL Version 2.
Be aware, that when using the package with the ``extjs`` extras, it will
install `Ext JS`_, which has different license policies. See
http://www.sencha.com/products/extjs/license/ for details.


Copyright
=========

This package is copyright by `4teamwork <http://www.4teamwork.ch/>`_.

``ftw.tabbedview`` is licensed under GNU General Public License, version 2.


.. _ftw.table: https://github.com/4teamwork/ftw.table
.. _example.conference: https://github.com/collective/example.conference
.. _Ext JS: http://www.sencha.com/products/extjs/
.. _collective.quickupload: https://github.com/collective/collective.quickupload
