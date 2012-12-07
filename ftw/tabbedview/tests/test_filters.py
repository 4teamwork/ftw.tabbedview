from DateTime import DateTime
from ftw.tabbedview.filters import DateFilter
from unittest2 import TestCase


class TestDateFilter(TestCase):

    def setUp(self):
        self.filter = DateFilter()
        self.column = {'column': 'created',
                       'column_title': 'Created',
                       'filter': self.filter}

    def test_default_value_is_None(self):
        self.assertEqual(self.filter.get_default_value({}), None)

    def test_get_filter_definition(self):
        self.assertEqual(self.filter.get_filter_definition(self.column, []),
                         {'type': 'date'})

    def test_apply_filter_to_query__no_filter(self):
        query = {}
        data = {'type': 'date', 'value': None}
        output = {}

        self.assertEqual(self.filter.apply_filter_to_query(
                self.column, query, data), output)

    def test_apply_filter_to_query__equals_day(self):
        query = {}
        data = {'type': 'date', 'value': {'eq': '2012-12-15'}}
        output = {'created': {'range': 'min:max',
                              'query': (DateTime('2012-12-15 00:00:00'),
                                        DateTime('2012-12-15 23:59:59'))}}

        self.assertEqual(self.filter.apply_filter_to_query(
                self.column, query, data), output)

    def test_create_query_value__no_filter(self):
        self.assertEqual(self.filter._create_query_value(None), None)
        self.assertEqual(self.filter._create_query_value(''), None)

    def test_create_query_value__range(self):
        input = {'gt': '2012-12-13',
                 'lt': '2012-12-18'}

        output = {'range': 'min:max',
                  'query': (DateTime('2012-12-13 00:00:00'),
                            DateTime('2012-12-18 23:59:59'))}

        self.assertEqual(self.filter._create_query_value(input), output)

    def test_create_query_value__after(self):
        input = {'gt': '2012-12-13'}

        output = {'range': 'min',
                  'query': DateTime('2012-12-13 00:00:00')}

        self.assertEqual(self.filter._create_query_value(input), output)

    def test_create_query_value__before(self):
        input = {'lt': '2012-12-18'}

        output = {'range': 'max',
                  'query': DateTime('2012-12-18 23:59:59')}

        self.assertEqual(self.filter._create_query_value(input), output)

    def test_create_query_value__equals(self):
        input = {'eq': '2012-12-15'}

        output = {'range': 'min:max',
                  'query': (DateTime('2012-12-15 00:00:00'),
                            DateTime('2012-12-15 23:59:59'))}

        self.assertEqual(self.filter._create_query_value(input), output)

    def test_create_query_value__empty(self):
        input = {}
        output = None
        self.assertEqual(self.filter._create_query_value(input), output)

    def test_format_value_for_extjs__eq(self):
        input = {'type': 'date',
                 'value': {'eq': '2012-10-30'}}

        output = {'type': 'date',
                  'value': {'on': '10/30/2012'}}

        self.assertEqual(self.filter.format_value_for_extjs(input), output)

    def test_format_value_for_extjs__lt(self):
        input = {'type': 'date',
                 'value': {'lt': '2012-10-30'}}

        output = {'type': 'date',
                  'value': {'before': '10/30/2012'}}

        self.assertEqual(self.filter.format_value_for_extjs(input), output)

    def test_format_value_for_extjs__gt(self):
        input = {'type': 'date',
                 'value': {'gt': '2012-10-30'}}

        output = {'type': 'date',
                  'value': {'after': '10/30/2012'}}

        self.assertEqual(self.filter.format_value_for_extjs(input), output)
