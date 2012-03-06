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


Usage
=====

Default table implementation
----------------------------

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


Ext JS table implementation
---------------------------

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


Licensing
---------

This package is released under GPL Version 2.
Be aware, that when using the package with the ``extjs`` extras, it will
install `Ext JS`_, which has different license policies. See
http://www.sencha.com/products/extjs/license/ for details.


Links
=====

- Main github project repository: https://github.com/4teamwork/ftw.tabbedview
- Issue tracker: https://github.com/4teamwork/ftw.tabbedview/issues
- Package on pypi: http://pypi.python.org/pypi/ftw.tabbedview


Maintainer
==========

This package is produced and maintained by `4teamwork <http://www.4teamwork.ch/>`_ company.


.. _ftw.table: https://github.com/4teamwork/ftw.table
.. _Ext JS: http://www.sencha.com/products/extjs/
