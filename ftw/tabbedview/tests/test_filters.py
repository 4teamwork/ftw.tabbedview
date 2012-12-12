from DateTime import DateTime
from ftw.tabbedview.filters import CatalogUniqueValueFilter
from ftw.tabbedview.filters import DateFilter
from ftw.testing import MockTestCase
from plone.memoize import ram
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


class TestCatalogUniqueValueFilter(MockTestCase):

    def setUp(self):
        super(TestCatalogUniqueValueFilter, self).setUp()
        self.filter = CatalogUniqueValueFilter()
        self.column = {'column': 'Subject',
                       'column_title': 'Subject',
                       'filter': self.filter}

        ram.global_cache.invalidateAll()

        self.catalog = self.mocker.mock()
        self.mock_tool(self.catalog, 'portal_catalog')

    def test_get_default_value__is_None(self):
        self.replay()
        self.assertEquals(self.filter.get_default_value(self.column), None)

    def test_get_filter_definition(self):
        contents = []
        self.expect(self.catalog.uniqueValuesFor('Subject')).result([
                'Foo', 'Bar'])

        self.replay()

        output = {'type': 'list',
                  'options': ['Bar', 'Foo']}

        self.assertEquals(self.filter.get_filter_definition(
                self.column, contents), output)

    def test_apply_filter_to_query(self):
        query = {'path': '..'}
        data = {'type': 'list', 'value': ['Foo', 'Baz']}

        self.replay()

        output = {'path': '..',
                  'Subject': ['Foo', 'Baz']}

        self.assertEquals(self.filter.apply_filter_to_query(
                self.column, query, data), output)

        def test_format_value_for_extjs(self):
            self.replay()

            input = output = object()
            self.assertEquals(self.filter.format_value_for_extjs(input),
                              output)

    def test_get_options(self):
        self.expect(self.catalog.uniqueValuesFor('Subject')).result([
                'Foo', 'Bar', 'Baz'])

        self.replay()

        self.assertEqual(self.filter._get_options('Subject'), [
                'Bar', 'Baz', 'Foo'])

    def test_get_options__cached(self):
        self.expect(self.catalog.uniqueValuesFor('Subject')).result([
                'Foo', 'Bar', 'Baz']).count(1)

        self.replay()

        self.assertEqual(self.filter._get_options('Subject'), [
                'Bar', 'Baz', 'Foo'])

        self.assertEqual(self.filter._get_options('Subject'), [
                'Bar', 'Baz', 'Foo'])

    def test_get_options__cached_per_column_id(self):
        self.expect(self.catalog.uniqueValuesFor('foo')).result([
                1, 2]).count(1)
        self.expect(self.catalog.uniqueValuesFor('bar')).result([
                3, 4]).count(1)

        self.replay()

        self.assertEqual(self.filter._get_options('foo'), [1, 2])
        self.assertEqual(self.filter._get_options('foo'), [1, 2])
        self.assertEqual(self.filter._get_options('bar'), [3, 4])
        self.assertEqual(self.filter._get_options('bar'), [3, 4])
        self.assertEqual(self.filter._get_options('foo'), [1, 2])
