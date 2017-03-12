import requests
import flask

app = flask.Flask(__name__)
app.config.from_pyfile('settings.py')

@app.route('/collection.json')
def collection():
    return flask.jsonify({
        'feed': 'feed.json',
    })

def format_document(doc):
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

if __name__ == "__main__":
    app.run(debug=True)
