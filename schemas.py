REPORT = {
    'type': 'object',
    'properties': {
        'name': {'type': 'string'},
        'last_seen_location': {
            'type': 'array',
            'items': [{'type': 'number'}, {'type': 'number'}],
        },
        'age': {'type': 'number'},
        'clothing': {'type': 'string'},
        'notes': {'type': 'string'},
    },
    'required': ['name', 'last_seen_location', 'age']
}
