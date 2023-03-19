from flask import Flask, request, render_template
from flask_cors import CORS
from elasticsearch import Elasticsearch


es = Elasticsearch(hosts=["http://127.0.0.1:9200"])
app = Flask(__name__)
CORS(app)
MAX_SIZE = 150

@app.route("/query")
def search_query():
    query = request.args["q"].lower()   
    tokens = query.split(" ")

    keys = [
        {
            "span_multi": {
                "match": {"fuzzy": {"topic": {"value": i, "fuzziness": "AUTO"}}}
            }
        }
        for i in tokens
    ]
    content = {
        "query":{
            "bool": {
                "must": [{"span_near": {"clauses": keys, "slop": 0, "in_order": False}}]
            }
        },
        "size":MAX_SIZE
    }
    resp = es.search(index = "mywebsites", body = content, size = MAX_SIZE)
    res = [result['_source'] for result in resp['hits']['hits']]
    print(res)
    return res

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)


