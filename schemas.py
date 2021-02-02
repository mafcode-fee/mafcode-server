REPORT = {
    'type': 'object',
    'properties': {
        'name': {'type': 'string'},
        'last_seen_location': {
            'type': 'object',
            'properties': {
                'lat': {'type': 'number'},
                'lng': {'type': 'number'},
            },
            'required': ['lat', 'lng']
        },
        'age': {'type': 'number'},
        'clothing': {'type': 'string'},
        'notes': {'type': 'string'},
    },
    'required': ['name', 'last_seen_location', 'age']
}
