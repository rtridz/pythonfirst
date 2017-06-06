API_TOKEN = '',
BOT_NAME = '',
ADMIN_ID = '',

shortcuts = {
    'МОСКВА': [
        'мск',
        'м',
    ],
    'САНКТ-ПЕТЕРБУРГ': [
        'спб',
        'сп',
        'п',
        'с',
    ],
}

QUERY_REGEXP_LIST = [
    r'(?P<from>[^,]+)\s*,\s*(?P<to>[^,]+)\s*,\s*(?P<when>.*)',
    r'(?P<from>[^\s]+)\s+(?P<to>[^\s]+)(?P<when>.*)',
]