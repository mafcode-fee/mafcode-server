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
    'required': ['name', 'age']
}


REGISTER = {
    'type': 'object',
    'properties':{
        'email' :{
            'type':'string',
            'pattern':'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$'
        },
        'password' :{
            'description':"password must be at least 8 chars, & must contain lowerCase & upperCase letters, & numbers",
            'type':'string',
            'minLength':8,
            'maxLength':20,
            'pattern':'^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)'
        },
        'first_name' :{
            'type':'string',
        },
        'last_name' :{
            'type':'string',
        },
    },
    'required':['email','password']
}