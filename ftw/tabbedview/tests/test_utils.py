from ftw.tabbedview.interfaces import IExtFilter
from ftw.tabbedview.utils import get_column_filter_types_and_defaults
from ftw.tabbedview.utils import get_filter_values
from ftw.tabbedview.utils import get_filters_from_request
from ftw.tabbedview.utils import get_filters_from_state
from unittest2 import TestCase
from zope.interface import implements


class DummyRequest(object):

    def __init__(self, form):
        self.form = form


class FooList(object):
    implements(IExtFilter)

    def get_default_value(self, column):
        return [u'Foo']

    def get_filter_definition(self, column, contents):
        return {'type': 'list',
                'options': [u'Foo', u'Bar', 'Baz']}

    def apply_filter_to_query(self, column, query, data):
        return query


class BarDate(object):
    implements(IExtFilter)

    def get_default_value(self, column):
        return {'eq': '2000-10-25'}

    def get_filter_definition(self, column, contents):
        return {'type': 'date'}

    def apply_filter_to_query(self, column, query, data):
        return query


class BazList(object):
    implements(IExtFilter)

    def get_default_value(self, column):
        return None

    def get_filter_definition(self, column, contents):
        return {'type': 'list',
                'options': []}

    def apply_filter_to_query(self, column, query, data):
        return query


COLUMNS = [(u'id'),

           {'column': 'foo',
            'filter': FooList()},

           {'column': 'bar',
            'filter': BarDate()},

           {'column': 'blubb'},

           {'column': 'baz',
            'filter': BazList()}]


class TestGetFilterValues(TestCase):

    def test_first_priority_is_filter_state(self):
        req = DummyRequest({
                'filter[0][data][comparison]': 'lt',
                'filter[0][data][type]': 'date',
                'filter[0][data][value]': '12/31/2012',
                'filter[0][field]': 'bar',
                'filter[1][data][comparison]': 'gt',
                'filter[1][data][type]': 'date',
                'filter[1][data][value]': '12/11/2012',
                'filter[1][field]': 'bar'})

        # WAWRNING: Extjs has an timezone offset of 1 hour in the
        # filter state. Therfore it is the day before the selected!
        filter_state = {u'bar': {u'after': u'2012-12-12T23:00:00.000Z',
                                 u'before': u'2012-12-17T23:00:00.000Z'}}

        output = {'bar': {
                'type': 'date',
                'value': {
                    'gt': '2012-12-13',
                    'lt': '2012-12-18'}}}

        self.assertEqual(get_filter_values(COLUMNS, req, filter_state),
                         output)

    def test_second_priority_is_request(self):
        req = DummyRequest({
                'filter[0][data][comparison]': 'lt',
                'filter[0][data][type]': 'date',
                'filter[0][data][value]': '12/31/2012',
                'filter[0][field]': 'bar',
                'filter[1][data][comparison]': 'gt',
                'filter[1][data][type]': 'date',
                'filter[1][data][value]': '12/11/2012',
                'filter[1][field]': 'bar'})

        filter_state = None

        output = {'bar': {
                'type': 'date',
                'value': {
                    'gt': '2012-12-11',
                    'lt': '2012-12-31'}}}

        self.assertEqual(get_filter_values(COLUMNS, req, filter_state),
                         output)

    def test_third_priority_is_default_value(self):
        req = DummyRequest({})
        filter_state = None

        output = {
            'bar': {
                'type': 'date',
                'value': {
                    'eq': '2000-10-25'}},

            'foo': {
                'type': 'list',
                'value': [u'Foo']}}

        self.assertEqual(get_filter_values(COLUMNS, req, filter_state),
                         output)

    def test_empty_filter_state_overrides_default_filter(self):
        # necessary for disabling default filters
        req = DummyRequest({})
        filter_state = {}

        output = {}

        self.assertEqual(get_filter_values(COLUMNS, req, filter_state),
                         output)


class TestGetFiltersFromRequest(TestCase):

    def test_request_form_is_none(self):
        req = DummyRequest(None)
        self.assertEqual(get_filters_from_request(req), None)

    def test_request_form_is_empty(self):
        req = DummyRequest({})
        self.assertEqual(get_filters_from_request(req), None)

    def test_simple_filter_extraction(self):
        req = DummyRequest({
                'filter[0][field]': 'foo',
                'filter[0][data][type]': 'string',
                'filter[0][data][value]': 'Foo'})

        self.assertEqual(get_filters_from_request(req),
                         {'foo': {'type': 'string',
                                  'value': 'Foo'}})

    def test_multiple_filter_extraction(self):
        req = DummyRequest({
                'filter[0][field]': 'foo',
                'filter[0][data][type]': 'string',
                'filter[0][data][value]': 'Foo',

                'filter[1][field]': 'bar',
                'filter[1][data][type]': 'string',
                'filter[1][data][value]': 'Bar'})

        self.assertEqual(get_filters_from_request(req),
                         {'foo': {'type': 'string',
                                  'value': 'Foo'},

                          'bar': {'type': 'string',
                                  'value': 'Bar'}})

    def test_list_extraction(self):
        # Zope parses the value of list filters already as
        # list. See the magic?
        req = DummyRequest({
                'filter[0][field]': 'foo',
                'filter[0][data][type]': 'list',
                'filter[0][data][value]': ['bar', 'baz']})

        self.assertEqual(get_filters_from_request(req),
                         {'foo': {'type': 'list',
                                  'value': ['bar', 'baz']}})

    def test_date_exctraction(self):
        # Date values may have multiple constrains, suche
        # as date lower and date greater in combination.
        # Therfore with a list of constrains as value.
        # We also use date objects.

        req = DummyRequest({
                'filter[0][data][comparison]': 'lt',
                'filter[0][data][type]': 'date',
                'filter[0][data][value]': '12/31/2012',
                'filter[0][field]': 'modified',
                'filter[1][data][comparison]': 'gt',
                'filter[1][data][type]': 'date',
                'filter[1][data][value]': '12/11/2012',
                'filter[1][field]': 'modified'})

        data = get_filters_from_request(req)

        self.assertEqual(
            data,
            {'modified':
                 {'type': 'date',
                  'value': {
                        'gt': '2012-12-11',
                        'lt': '2012-12-31'}}})


class TestGetFiltersFromState(TestCase):

    def test_no_state_results_in_None(self):
        input = None
        output = None

        self.assertEqual(get_filters_from_state(COLUMNS, input), output)

    def test_list(self):
        input = {u'foo': [u'Bar', u'Baz']}
        output = {'foo': {'type': 'list',
                          'value': ['Bar', 'Baz']}}

        self.assertEqual(get_filters_from_state(COLUMNS, input), output)

    def test_date_range(self):
        # WAWRNING: Extjs has an timezone offset of 1 hour in the
        # filter state. Therfore it is the day before the selected!
        input = {u'bar': {u'after': u'2012-12-12T23:00:00.000Z',
                          u'before': u'2012-12-17T23:00:00.000Z'}}

        output = {'bar': {
                'type': 'date',
                'value': {
                    'gt': '2012-12-13',
                    'lt': '2012-12-18'}}}

        self.assertEqual(get_filters_from_state(COLUMNS, input), output)

    def test_date_after(self):
        # WAWRNING: Extjs has an timezone offset of 1 hour in the
        # filter state. Therfore it is the day before the selected!
        input = {u'bar': {u'after': u'2012-12-12T23:00:00.000Z'}}

        output = {'bar': {
                'type': 'date',
                'value': {
                    'gt': '2012-12-13'}}}

        self.assertEqual(get_filters_from_state(COLUMNS, input), output)

    def test_date_on(self):
        input = {u'bar': {u'on': u'2012-12-13T23:00:00.000Z'}}

        output = {'bar': {
                'type': 'date',
                'value': {
                    'eq': '2012-12-14'}}}

        self.assertEqual(get_filters_from_state(COLUMNS, input), output)


class TestGetColumnFilterTypesAndDefaults(TestCase):

    def test_get_column_filter_types_and_defaults(self):
        output = {'foo': ('list', [u'Foo']),
                  'bar': ('date', {'eq': '2000-10-25'}),
                  'baz': ('list', None)}

        self.assertEqual(get_column_filter_types_and_defaults(COLUMNS),
                         output)
