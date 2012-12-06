from datetime import datetime
from ftw.tabbedview.utils import get_filters_from_request
from unittest2 import TestCase


class DummyRequest(object):

    def __init__(self, form):
        self.form = form


class TestGetFiltersFromRequest(TestCase):

    # def test_request_form_is_none(self):
    #     req = DummyRequest(None)
    #     self.assertEqual(req, {})

    def test_request_form_is_empty(self):
        req = DummyRequest({})
        self.assertEqual(get_filters_from_request(req), {})

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
                        'gt': datetime(2012, 12, 11),
                        'lt': datetime(2012, 12, 31)}}})
