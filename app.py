from datetime import datetime as dt
from environs import env
from flask import Flask, jsonify, render_template, request
from cozymeal import articles as cza, emails as cze, utils as czu, settings

env.read_env()

app = Flask(__name__)
 
@app.get("/")
def render_home_page():
    date_a_week_ago = czu.get_date_a_week_ago()
    last_checked_str = date_a_week_ago.strftime("%m/%d/%Y")
    articles = cza.get_new_articles(date_a_week_ago)

    return render_template(
        'home.html',
        articles = articles,
        last_checked = last_checked_str,
    )

@app.post("/")
def email_for_new_articles():
    if not czu.verify_token(request):
        return jsonify({"error": "Unauthorized - Invalid or missing token"}), 401

    last_checked = czu.get_last_checked()
    if not last_checked:
        last_checked = czu.get_date_a_week_ago()

    articles = list(cza.get_new_articles(last_checked))
    if not articles:
        return '', 204

    cze.send_email_for_articles(articles)

    last_checked = dt.now(settings.DEFAULT_TZ)
    czu.set_last_checked(last_checked)

    return jsonify({"status": "success"}), 200