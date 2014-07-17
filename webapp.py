import logging
from urllib.parse import quote as qs_quote
import pyes
from pyes import TermFilter
from flask import Flask, render_template, jsonify, request

import esutils
import config

from utils import validate_int


app = Flask(__name__)
app.config.update(
    {k: getattr(config, k) for k in dir(config) if k == k.upper()}
)
log = logging.getLogger(__name__)


@app.route("/")
def index_view():
    return render_template('index.html')


def build_search_url(query, page=1):
    url = '#/search/{}'.format(qs_quote(query))
    if page > 1:
        url += '/page/{}'.format(qs_quote(str(page)))
    return url


@app.route("/query")
def query_view():
    page_size = 10
    es = esutils.get_es()
    user_query = None
    query = pyes.MatchAllQuery()
    if 'q' in request.values:
        user_query = request.values['q']
        query = esutils.construct_text_query(user_query)
    search = pyes.Search(query)
    search.size = page_size

    page = validate_int(request.values.get('page', 1),
                        vmin=1, vmax=100*1000, default=1)
    search.start = (page - 1) * page_size

    if request.values.get('licence_sane', '').strip():
        search.filter = TermFilter('licence_sane',
                                   request.values['licence_sane'])

    licence_agg = pyes.aggs.TermsAgg('licences', field='licence_sane', size=0)
    if search.filter is not None:
        query_agg = pyes.aggs.FilterAgg('query_facets', search.filter)
        query_agg.sub_aggs = [licence_agg]
        search.agg.add(query_agg)
    else:
        search.agg.add(licence_agg)

    results = es.search(search, indices=config.ES_INDEX,
                        doc_types=config.ES_INDEX)
    pagination = {
        'current': search.start // search.size + int(bool(search.start % search.size)) + 1,
        'total': results.total // search.size + int(bool(results.total % search.size)),
    }
    if pagination['total'] > 1:
        if pagination['current'] > 1:
            pagination['prev_url'] = build_search_url(user_query, page=pagination['current'] - 1)
        if pagination['current'] < pagination['total']:
            pagination['next_url'] = build_search_url(user_query, page=pagination['current'] + 1)
    data = {
        'docs': list(results),
        'total': results.total,
        'facets': results.aggs,
        'pagination': pagination,
    }
    if 'query_facets' in data['facets']:
        for k, v in data['facets']['query_facets'].items():
            if v != 'doc_count':
                data['facets'][k] = v
        del data['facets']['query_facets']
    return jsonify(data)


if __name__ == "__main__":
    app.run()
