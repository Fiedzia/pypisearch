import pyes

import config

es_conn = None


def get_es():
    global es_conn
    if es_conn is None:
        es_conn = pyes.ES(config.ES)
    return es_conn


def create_index():
    es = get_es()
    es.indices.create_index_if_missing(
        config.ES_INDEX,
        settings=config.ES_INDEX_SETTINGS)
    es.indices.put_mapping(
        doc_type=config.ES_DOC_TYPE,
        mapping=config.ES_MAPPING,
        indices=config.ES_INDEX)


def construct_text_query(q):
    query = pyes.QueryStringQuery(
        q,
        #totally made up numbers, but I want summary to be less influential
        search_fields=['name^10', 'summary^6', 'description^0.5'],
        allow_leading_wildcard=False,
        default_operator='AND')
    return query


def set_refresh(enabled=True):
    value = -1
    if enabled:
        value = config.ES_INDEX_SETTINGS['index']['refresh_interval']
    es = get_es()
    es.indices.update_settings(config.ES_INDEX, {'index': {'refresh_interval': value}})
