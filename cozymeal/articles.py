import requests
import json

from bs4 import BeautifulSoup
from bs4.element import Script
from datetime import datetime as dt
from html import unescape
from itertools import count

BASE_ARCHIVE_URL = "https://www.cozymeal.com/magazine/authors/sarah-salisbury"

class Article:
    def __init__(self, title: str, url: str, date_published: dt):
        self.title = title
        self.url = url
        self.date_published = date_published

    def get_pretty_title(self):
        return unescape(self.title)

    def get_pretty_date(self):
        return self.date_published.strftime("%m/%d/%Y")

    def __str__(self):
        return f"{self.get_pretty_title()} ({self.get_pretty_date()})"

def _get_date_published(script_data: dict) -> dt:
    date_published_raw = script_data["datePublished"]
    date_published = dt.fromisoformat(date_published_raw)
    return date_published

def _get_article_from_script(script: Script) -> Article | None:
    text: str = script.text.strip(" \n")
    script_data = json.loads(text)

    try:
        title = script_data["name"]
        url = script_data["mainEntityOfPage"]["@id"]
        date_published = _get_date_published(script_data)
    except (KeyError, ValueError):
        return None

    return Article(title, url, date_published)

def _get_articles_from_archive_page(page: int) -> list[Article]:
    archive_response = requests.get(f"{BASE_ARCHIVE_URL}?page={page}")
    try:
        archive_response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        return []
    raw_data = archive_response.text

    soup = BeautifulSoup(raw_data, "html.parser")
    scripts = filter(lambda s: "Sarah" in s.text, soup.find_all("script"))

    page_of_articles = []
    for script in scripts:
        article = _get_article_from_script(script)
        if not article:
            continue

        page_of_articles.append(article)

    return page_of_articles

def get_articles() -> list[Article]:
    articles = []
    for i in count(start=1):
        page_of_articles = _get_articles_from_archive_page(i)
        if not page_of_articles:
            break

        articles.extend(page_of_articles)

    return articles

def get_new_articles(last_checked) -> filter:
    articles = get_articles()
    sorted_articles = sorted(articles, key=lambda a: a.date_published, reverse=True)
    filtered_articles = filter(lambda a: a.date_published >= last_checked, sorted_articles)

    return filtered_articles