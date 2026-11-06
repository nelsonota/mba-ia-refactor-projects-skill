from flask import request


class InvalidRequestData(Exception):
    pass


FIELD_TYPES = {
    'task': {
        'title': str, 'description': str, 'status': str, 'priority': int,
        'user_id': int, 'category_id': int, 'due_date': str,
    },
    'user': {
        'name': str, 'email': str, 'password': str, 'role': str,
        'active': bool,
    },
    'category': {'name': str, 'description': str, 'color': str},
}


def read_json_object(domain):
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        raise InvalidRequestData()

    for field, expected_type in FIELD_TYPES[domain].items():
        if field not in payload or payload[field] is None:
            continue
        value = payload[field]
        if expected_type is int:
            valid = type(value) is int
        elif expected_type is bool:
            valid = type(value) is bool
        else:
            valid = isinstance(value, expected_type)
        if not valid:
            raise InvalidRequestData()

    if domain == 'task' and 'tags' in payload and payload['tags'] is not None:
        tags = payload['tags']
        if not isinstance(tags, str) and not (
            isinstance(tags, list) and all(isinstance(tag, str) for tag in tags)
        ):
            raise InvalidRequestData()
    return payload


def read_task_search_args():
    query_args = request.args.to_dict()
    for field in ('priority', 'user_id'):
        if query_args.get(field):
            try:
                query_args[field] = int(query_args[field])
            except (TypeError, ValueError):
                raise InvalidRequestData() from None
    return query_args
