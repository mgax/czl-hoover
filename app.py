import requests
import flask

app = flask.Flask(__name__)
app.config.from_pyfile('settings.py')

def fix_diacritics(text):
    return (text
        .replace('ş', 'ș')
        .replace('Ş', 'Ș')
        .replace('ţ', 'ț')
        .replace('Ţ', 'Ț')
    )

@app.route('/collection.json')
def collection():
    return flask.jsonify({
        'feed': 'feed.json',
        'data_urls': 'doc/{id}',
    })

def format_document(doc):
    for field in ['title', 'description']:
        doc[field] = fix_diacritics(doc[field])
    return {
        'id': doc['id'],
        'version': doc['_created_at'],
        'content': doc,
    }

@app.route('/feed.json')
def feed(cursor=None):
    cursor = flask.request.args.get('cursor')
    czl_api_url = flask.current_app.config['CZL_API_URL'] + 'publications/'
    if cursor:
        czl_api_url += '?cursor=' + cursor
    czl_page = requests.get(czl_api_url).json()
    documents = [format_document(doc) for doc in czl_page['results']]
    if czl_page['next']:
        czl_next_cursor = czl_page['next'].split('=')[-1]
        next_url = 'feed.json?cursor=' + czl_next_cursor
    else:
        next_url = None
    return flask.jsonify({
        'documents': documents,
        'next': next_url,
    })

@app.route('/doc/<path:doc_id>')
def doc(doc_id):
    czl_api_url = flask.current_app.config['CZL_API_URL']
    czl_doc_url = czl_api_url + 'publications/' + doc_id
    resp = requests.get(czl_doc_url).json()
    return flask.jsonify(format_document(resp))

if __name__ == "__main__":
    app.run(debug=True)
