from datetime import datetime as dt
from flask import Flask, jsonify, render_template
from cozymeal import articles as cza, emails as cze

app = Flask(__name__)
 
@app.get("/")
def render_home_page():
    date_a_week_ago = cza.get_date_a_week_ago()
    last_checked_str = date_a_week_ago.strftime("%m/%d/%Y")
    articles = cza.get_new_articles(date_a_week_ago)
    return render_template(
        'home.html',
        articles = articles,
        last_checked = last_checked_str,
    )

@app.post("/")
def email_for_new_articles():
    last_checked = cza.get_last_checked()
    last_checked = None
    if not last_checked:
        last_checked = cza.get_date_a_week_ago()

    articles = list(cza.get_new_articles(last_checked))
    if not articles:
        # Don't update last_checked in case any articles 
        # get published with a backlogged date
        return '', 204 

    cze.send_email_for_articles(articles)

    last_checked = dt.now(cza.LAX_TZ)
    cza.set_last_checked(last_checked)

    return jsonify({"status": "success"}), 200