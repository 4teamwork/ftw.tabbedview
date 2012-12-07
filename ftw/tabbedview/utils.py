from datetime import datetime
from datetime import timedelta
import re


def get_filter_values(columns, request, filter_state):
    """Parses the request, the personal filter_state (gridstate['filter'])
    and the default filter values and returns a dict of the current filters
    to be used.

    Example return value:
    >>> {'getResponsibleManager': {'type': 'list',
    ...                            'value': ['foo', 'bar']},
    ...  'modified': {'type': 'date',
    ...               'value': {
    ...                   'gt': '2012-12-11',
    ...                   'lt': '2012-12-31'}}}
    """

    state_filters = get_filters_from_state(columns, filter_state)
    if state_filters is not None:
        return state_filters

    request_filters = get_filters_from_request(request)
    if request_filters is not None:
        return request_filters

    values = {}
    types_and_defaults = get_column_filter_types_and_defaults(columns)

    for name in types_and_defaults.keys():
        type_, default = types_and_defaults[name]
        if default is None:
            continue

        values[name] = {'type': type_,
                        'value': default}

    return values


def get_filters_from_request(request):
    """This helper function helps extracting the currently
    active filters from the request. Since the ExtJS filter
    uses request keys which are not automatically parseable
    by Zope, we need to apply some magic.

    Example return value:
    >>> {'getResponsibleManager': {'type': 'list',
    ...                            'value': ['foo', 'bar']}}

    """

    if not request.form:
        return None

    data = {}

    for key, value in request.form.items():
        # keys are in form "filter[0][data][type]"

        if not key.startswith('filter['):
            continue

        key = key.replace('[data]', '')
        match = re.match(r'filter\[(\d)\]\[(.*?)\]', key)
        if not match:
            continue

        index = match.groups()[0]
        name = match.groups()[1]

        if index not in data:
            data[index] = {}
        data[index][name] = value


    filters = {}

    def convert_date(datestr):
        # convert from %m/%d/%Y to %Y-%m-%d
        return re.sub(r'^(\d{2})/(\d{2})/(\d{4})$',
                      r'\g<3>-\g<1>-\g<2>',
                      datestr)

    for item in data.values():
        field = item.get('field')
        type_ = item.get('type')

        if field not in filters:
            filters[field] = {
                'type': type_}

        if type_ == 'date':
            if 'value' not in filters[field]:
                filters[field]['value'] = {}

            comparison = item.get('comparison')
            filters[field]['value'][comparison] = convert_date(item['value'])

        else:
            filters[field]['value'] = item.get('value')

    return filters or None


def get_filters_from_state(columns, filter_state):
    if filter_state is None:
        return None

    types_and_defaults = get_column_filter_types_and_defaults(columns)

    result = {}

    def convert_date(datestr):
        # XXX: the date in the persistent filter state is the day before at
        # 23:00, because of an timezone offset. We fix it manually here.
        # convert from: '2012-12-17T23:00:00.000Z'
        # to: '2012-12-18'

        # remove ".000Z" at the end
        datestr = datestr.split('.')[0]

        # parse and fix offset
        date = datetime.strptime(datestr, '%Y-%m-%dT%H:%M:%S')
        date += timedelta(hours=1)

        # format
        return date.strftime('%Y-%m-%d')

    for key, value in filter_state.items():
        if key not in types_and_defaults:
            continue

        type_, _default = types_and_defaults[key]

        if type_ == 'date':
            date_value = {}

            if 'before' in value:
                date_value['lt'] = convert_date(value['before'])

            if 'after' in value:
                date_value['gt'] = convert_date(value['after'])

            if 'on' in value:
                date_value['eq'] = convert_date(value['on'])

            value = date_value

        result[key] = {'type': type_,
                       'value': value}

    return result


def get_column_filter_types_and_defaults(columns):
    filters = {}

    for col in columns:
        if not isinstance(col, dict):
            continue

        col_id = col.get('column')
        if not col_id:
            continue

        filter_ = col.get('filter')
        if not filter_:
            continue

        definition = filter_.get_filter_definition(col, [])
        if not definition or not definition.get('type'):
            continue

        default = filter_.get_default_value(col)
        filters[col_id] = (definition['type'], default)

    return filters
