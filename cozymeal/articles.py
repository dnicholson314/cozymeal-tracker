import re
import requests

from bs4 import BeautifulSoup
from bs4.element import Script
from cozymeal import settings
from datetime import datetime as dt
from environs import env
from html import unescape
from itertools import count

BASE_ARCHIVE_URL = "https://www.cozymeal.com/magazine/authors/sarah-salisbury"
NAME_REGEX_STR = r'(?<="name" \: ").+(?=",)'
URL_REGEX_STR = r'(?<="@id": ").+(?=")'
DATE_REGEX_STR = r'(?<="datePublished": ").+(?=",)'

class Article:
    def __init__(self, title: str, url: str, date_published: dt):
        self.title = title
        self.url = url
        self.date_published = date_published

    def get_pretty_title(self):
        return unescape(self.title)

    def get_pretty_date(self):
        return self.date_published.strftime("%m/%d/%Y")

def _get_date_published(text: str) -> dt:
    date_published_raw = re.search(DATE_REGEX_STR, text).group()
    date_published = dt.fromisoformat(date_published_raw)
    return date_published

def _get_article_from_script(script: Script) -> Article:
    text: str = script.text

    title = re.search(NAME_REGEX_STR, text).group()
    url = re.search(URL_REGEX_STR, text).group()
    date_published = _get_date_published(text)

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

def get_new_articles(last_checked) -> list[Article]:
    articles = get_articles()
    sorted_articles = sorted(articles, key=lambda a: a.date_published, reverse=True)
    filtered_articles = filter(lambda a: a.date_published >= last_checked, sorted_articles)

    return filtered_articles