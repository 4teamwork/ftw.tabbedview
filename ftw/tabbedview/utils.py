from datetime import datetime
import re


def get_filters_from_request(request):
    """This helper function helps extracting the currently
    active filters from the request. Since the ExtJS filter
    uses request keys which are not automatically parseable
    by Zope, we need to apply some magic.

    Example return value:
    >>> {'getResponsibleManager': {'type': 'list',
    ...                            'value': ['foo', 'bar']}}

    """

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

    return filters
