import json
import pytz
import re
import requests

from bs4 import BeautifulSoup
from bs4.element import Script
from datetime import datetime as dt, timedelta as tdel
from environs import env
from html import unescape
from itertools import count
from json.decoder import JSONDecodeError
from pathlib import Path

env.read_env()

BASE_ARCHIVE_URL = "https://www.cozymeal.com/magazine/authors/sarah-salisbury"

NAME_REGEX_STR = r'(?<="name" \: ").+(?=",)'
URL_REGEX_STR = r'(?<="@id": ").+(?=")'
DATE_REGEX_STR = r'(?<="datePublished": ").+(?=",)'

LAST_CHECKED_DIR = env.path("LAST_CHECKED_DIR", default=Path("/data"))
LAST_CHECKED_DIR.mkdir(parents=True, exist_ok=True)

LAST_CHECKED_FILENAME = LAST_CHECKED_DIR / 'last_checked_time.json'
LAST_CHECKED_KEY = "last_checked_time"

LAX_TZ = pytz.timezone('America/Los_Angeles')

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

def get_date_a_week_ago(tz = LAX_TZ) -> dt:
    return dt.now(tz) - tdel(days=7)

def get_date_a_week_before(timestamp: dt) -> dt:
    return timestamp - tdel(days=7)

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

def set_last_checked(timestamp: dt) -> None:
    with open(LAST_CHECKED_FILENAME, 'w') as file:
        json.dump({LAST_CHECKED_KEY: timestamp.isoformat()}, file)

def get_last_checked() -> dt | None:
    try:
        with open(LAST_CHECKED_FILENAME, 'r') as file:
            data = json.load(file)
            return dt.fromisoformat(data[LAST_CHECKED_KEY])
    except (FileNotFoundError, KeyError, JSONDecodeError):
        return None