import smtplib, ssl

from cozymeal import settings
from cozymeal.articles import Article
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, PackageLoader, select_autoescape

jenv = Environment(
    loader=PackageLoader("cozymeal"),
    autoescape=select_autoescape()
)

PORT = 465
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
    message["From"] = settings.SENDER_EMAIL
    message["To"] = settings.RECEIVER_EMAIL
    message["Cc"] = settings.SENDER_EMAIL

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
        server.login(settings.SENDER_EMAIL, settings.EMAIL_PASSWORD)
        server.sendmail(settings.SENDER_EMAIL, settings.RECEIVER_EMAIL, message.as_string())
