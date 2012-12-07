from DateTime import DateTime
from ftw.tabbedview.interfaces import IExtFilter
from zope.interface import implements
import re


class DateFilter(object):
    implements(IExtFilter)

    def get_default_value(self, column):
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
