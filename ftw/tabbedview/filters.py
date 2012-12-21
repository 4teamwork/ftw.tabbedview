from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from ftw.tabbedview import tabbedviewMessageFactory as _
from ftw.tabbedview.interfaces import IExtFilter
from plone.memoize import ram
from time import time
from zope.component.hooks import getSite
from zope.interface import implements
import re


NEGATION_OPTION_KEY = '__negate-selected-list-options__'


def list_filter_negation_support(cls):
    """This class-decorator adds support for negation to list filters.
    It adds an option "[All but not the selected]" on top of the option list,
    which negates the selection automatically according to the options in the
    column definition.

    Usage on filter class:

    >>> @list_filter_negation_support
    ... class MyFancyListFilter(object):
    ...     implements(IExtFilter)
    ...     ...

    Usage per column:

    >>> columns = [{'column': 'foo',
    ...             'filter': list_filter_negation_support(MyListFilter)()}]
    """

    def get_filter_options_without_negation(definition):
        for item in definition['options']:
            if isinstance(item, (list, tuple)):
                key = item[0]
            else:
                key = item

            if key != NEGATION_OPTION_KEY:
                yield key

    # We apply the customization by subclassing the class and returning
    # the subclassed one, so that the original class does not get touched.
    # This allows to enable negation support per instance by using
    # list_filter_negation_support as wrapper rather than as class decorator.
    class __NegationSupport(cls):

        def get_filter_definition(self, *args, **kwargs):
            definition = cls.get_filter_definition(self, *args, **kwargs)
            assert definition.get('type') == 'list', \
                'Using list_filter_negation_support on non-list filter.'
            definition['options'].insert(0, (
                    NEGATION_OPTION_KEY, _(u'[All but not the selected]')))
            return definition

        def apply_filter_to_query(self, column, query, data):
            value = data.get('value')

            # When only the negation is enabled it means that we nothing
            # should be filtered, therefore we do not pass the call to the
            # wrapped implementation.
            # Single selection values may be a list of the key or the key
            # directly.
            if not value or value in (NEGATION_OPTION_KEY,
                                      [NEGATION_OPTION_KEY]):
                return query

            # Single selection values may be a list of the key or the key
            # directly.
            if not isinstance(value, list):
                value = [value]

            if value[0] == NEGATION_OPTION_KEY:
                definition = self.get_filter_definition(column, None)
                all = set(get_filter_options_without_negation(definition))

                excluding = set(value[1:])
                value = list(all - excluding)
                data['value'] = value

            return cls.apply_filter_to_query(self, column, query, data)

    __NegationSupport.__name__ = '%sWithNegationSupport' % cls.__name__
    return __NegationSupport


class DateFilter(object):
    """A generic date filter implementation.
    """

    implements(IExtFilter)

    def get_default_value(self, column):
        """Sets a default date filter, which can be changed by the user.

        Example return values:

        No default filter:
        >>> None

        Sepcific date:
        >>> {'eq': '2012-10-30'}

        Date range:
        >>> {'lt': '2012-10-15',
        ...  'gt': '2012-10-30'}
        """
        return None

    def get_filter_definition(self, column, contents):
        return {'type': 'date'}

    def apply_filter_to_query(self, column, query, data):
        value = self._create_query_value(data.get('value'))
        if value:
            column_id = column.get('column')

            query[column_id] = value
        return query

    def format_value_for_extjs(self, definition):
        value = definition.get('value')

        def convert_date(datestr):
            # convert from %Y-%m-%d to %m/%d/%Y
            return re.sub(r'^(\d{4})-(\d{2})-(\d{2})$',
                          r'\g<2>/\g<3>/\g<1>',
                          datestr)

        if not value:
            return definition

        if 'eq' in value:
            value['on'] = convert_date(value['eq'])
            del value['eq']

        if 'gt' in value:
            value['after'] = convert_date(value['gt'])
            del value['gt']

        if 'lt' in value:
            value['before'] = convert_date(value['lt'])
            del value['lt']

        return definition

    def _create_query_value(self, value):

        def convert(date, end_of_day=False):
            if end_of_day:
                date += ' 23:59:59'
            else:
                date += ' 00:00:00'

            return DateTime(date)

        if not isinstance(value, dict):
            return None

        elif 'lt' in value and 'gt' in value:
            return {'range': 'min:max',
                    'query': (convert(value['gt']),
                              convert(value['lt'], True))}

        elif 'gt' in value:
            return {'range': 'min',
                    'query': convert(value['gt'])}

        elif 'lt' in value:
            return {'range': 'max',
                    'query': convert(value['lt'], True)}

        elif 'eq' in value:
            return {'range': 'min:max',
                    'query': (convert(value['eq']),
                              convert(value['eq'], True))}

        else:
            return None


class CatalogUniqueValueFilter(object):
    """A generic list filter which gets the options from the catalog without
    using the result set. It also caches the results for an hour.
    """

    implements(IExtFilter)

    def get_default_value(self, column):
        return None

    def get_filter_definition(self, column, contents):
        column_id = column.get('column')
        values = self._get_options(column_id)

        return {'type': 'list',
                'options': values}

    def apply_filter_to_query(self, column, query, data):
        column_id = column.get('column')
        query[column_id] = data.get('value')
        return query

    def format_value_for_extjs(self, definition):
        return definition

    @ram.cache(lambda m, self, column_id: (
            self.__class__.__name__,
            m.__name__,
            time() // (60 * 60 * 10),
            column_id))
    def _get_options(self, column_id):
        catalog = getToolByName(getSite(), 'portal_catalog')

        values = []

        for value in catalog.uniqueValuesFor(column_id):
            values.append(value)

        values.sort()

        return values

CatalogUniqueValueFilterWithNegationSupport = list_filter_negation_support(
    CatalogUniqueValueFilter)
