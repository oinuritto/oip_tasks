from flask import Flask, request, render_template
from hw5.vector_search import VectorSearchEngine

app = Flask(__name__)
search_engine = VectorSearchEngine()


@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    query = ""

    if request.method == 'POST':
        query = request.form.get('query', '')
        if query.strip():
            results = search_engine.search(query)

    return render_template('index.html',
                           query=query,
                           results=results)


if __name__ == '__main__':
    app.run(debug=True)