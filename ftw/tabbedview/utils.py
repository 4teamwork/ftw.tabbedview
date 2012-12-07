from datetime import datetime
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
    ...                   'gt': datetime(2012, 12, 11),
    ...                   'lt': datetime(2012, 12, 31)}}}
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

    for item in data.values():
        field = item.get('field')
        type_ = item.get('type')

        if field not in filters:
            filters[field] = {
                'type': type_}

        if type_ == 'date':
            if 'value' not in filters[field]:
                filters[field]['value'] = {}

            date = datetime.strptime(item.get('value', ''), '%m/%d/%Y')
            comparison = item.get('comparison')
            filters[field]['value'][comparison] = date

        else:
            filters[field]['value'] = item.get('value')

    return filters or None


def get_filters_from_state(columns, filter_state):
    if filter_state is None:
        return None

    types_and_defaults = get_column_filter_types_and_defaults(columns)

    result = {}

    # The date may contain an hour (usually 23) because of the date range
    # manipulation in previously applied filters. We strip that, it will
    # be reapplied correctly afterwards. We only filter dates, no times.
    parse_date = lambda s: datetime.strptime(s.split('T', 1)[0], '%Y-%m-%d')

    for key, value in filter_state.items():
        if key not in types_and_defaults:
            continue

        type_, _default = types_and_defaults[key]

        if type_ == 'date':
            date_value = {}

            if 'before' in value:
                date_value['lt'] = parse_date(value['before'])

            if 'after' in value:
                date_value['gt'] = parse_date(value['after'])

            if 'on' in value:
                date_value['eq'] = parse_date(value['on'])

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
