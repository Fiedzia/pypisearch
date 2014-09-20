DEBUG = True
ES = 'http://localhost:9200/'
ES_INDEX = 'pypi'
ES_DOC_TYPE = 'pypi'

ES_INDEX_SETTINGS = {
    'index': {
        #raise this number if you care for the data and have more then one ES node
        'number_of_replicas': 0,
        'refresh_interval': '60s',
    },
    'analysis': {
        'tokenizer': {
            'pattern': {
                'type': 'pattern',
                'pattern': '([\w\+\-\.]+)',
                'group': 0,
            }
        },
        'analyzer': {
            'text': {
                'type': 'custom',
                'tokenizer': 'pattern',
                'filter': ['lowercase']
            }
        }
    }
}

"""
types: date(+format), integer, string, float, byte, short, integer, long,
       double, boolean,
index: analyzed|not_analyzed
term_vector: yes|no
analyzer, index_analyzer, search_analyze

"""

ES_MAPPING = {
    ES_DOC_TYPE: {
        'properties': {
            'description': {'type': 'string', 'analyzer': 'text'},
            'package_url': {'type': 'string', 'index': 'not_analyzed'},
            'licence': {'type': 'string', 'index': 'analyzed'},
            'licence_sane': {'type': 'string', 'index': 'not_analyzed'},
            'summary': {'type': 'string', 'analyzer': 'text'},
            'homepage': {'type': 'string', 'index': 'not_analyzed'},
            'version': {'type': 'string', 'index': 'not_analyzed'},
            'keywords': {'type': 'string'},
            'name': {'type': 'string', 'analyzer': 'text'},
            'name_suggest': {
                'type': 'completion',
                'payloads': True,
                'analyzer': 'text'
            },
            'downloads.last_month': {'type': 'integer'},
            'downloads.total': {'type': 'integer'},
            'latest_release': {'type': 'date'},
            #internal bookkeeping
            'run_id':  {'type': 'string', 'index': 'not_analyzed'},
        }
    }
}

