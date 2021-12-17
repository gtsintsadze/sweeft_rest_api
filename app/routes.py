from app import app
from flask import redirect, render_template
from app.models import Urls


@app.route('/<short_url>')
def redirection(short_url):
    long_url = Urls.query.filter_by(short=short_url).first()
    if long_url:
        long_url.increment_visited_count()
        return redirect(long_url.long)
    else:
        return '<h1>Not exists</h1>'
