from cozymeal.articles import Article
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from environs import env
from jinja2 import Environment, PackageLoader, select_autoescape

import smtplib, ssl

env.read_env()
jenv = Environment(
    loader=PackageLoader("cozymeal"),
    autoescape=select_autoescape()
)

PORT = 465
PASSWORD = env.str("EMAIL_PASSWORD")
SENDER_EMAIL = env.str("EMAIL_USERNAME")
RECEIVER_EMAIL = env.str("RECEIVER_EMAIL")

BASE_TEXT = """\
Some new articles were published from your backlog!
"""
BASE_HTML = jenv.get_template("email.html")
EMAIL_SUBJECT = "New Cozymeal Articles"

def _format_articles_for_email(articles: list[Article]) -> tuple[str, str]:
    text = BASE_TEXT
    for article in articles:
        text += "\n"
        text += f"{article.get_pretty_date()}: {article.get_pretty_title()} ({article.url})"

    html = BASE_HTML.render(articles=articles)

    return text, html

def get_message_for_email(articles: list[Article]) -> MIMEMultipart:
    message = MIMEMultipart("alternative")
    message["Subject"] = EMAIL_SUBJECT
    message["From"] = SENDER_EMAIL
    message["To"] = RECEIVER_EMAIL
    message["Cc"] = SENDER_EMAIL

    text, html = _format_articles_for_email(articles)

    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    message.attach(part1)
    message.attach(part2)

    return message

def send_email_for_articles(articles: list[Article]) -> None:
    context = ssl.create_default_context()
    message = get_message_for_email(articles)

    with smtplib.SMTP_SSL("smtp.gmail.com", PORT, context=context) as server:
        server.login(SENDER_EMAIL, PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, message.as_string())
