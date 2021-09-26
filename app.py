from flask import Flask, request, render_template
from urllib.parse import urlparse
from .storage import RedisStorage
app = Flask(__name__)
database = RedisStorage({'host':'localhost', 'db':0})


@app.route('/counter', methods=['GET', 'POST'])
def counter_page():
    origin = request.headers.get('Referer')
    error = None
    current = 0
    if origin is not None:
        try:
            current = database.increment_total_visits(origin)
        except Exception as err:
            error = f"Database error {str(err)}"
    else:
        error = "No Referer header in request for count"
    return render_template("counter.html", visitors_count=current, error=error)


@app.route('/test', methods=['GET', 'POST'])
def test_page():
    return render_template("test.html")


@app.route('/')
def main_page():
    return render_template("main.html", url=f'http{"s" if request.is_secure else ""}://{request.host}/counter')
