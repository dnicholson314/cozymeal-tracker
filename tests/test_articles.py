import pytest

from bs4 import BeautifulSoup
from datetime import datetime as dt, timedelta as tdelta
from cozymeal import articles, settings
from cozymeal.articles import Article
from json import JSONDecodeError
from pytest import MonkeyPatch
from requests import Response
from requests.exceptions import ConnectionError, HTTPError

TEST_TITLE = "Fish &amp; Chips"
TEST_PRETTY_TITLE = "Fish & Chips"
TEST_URL = "https://google.com"
TEST_DATE_PUBLISHED = dt(2023, 1, 1, tzinfo=settings.DEFAULT_TZ)
TEST_PRETTY_DATE = "01/01/2023"

TEST_ARTICLE_PAGE = ...

@pytest.fixture
def mock_article() -> Article:
    test_article = Article(TEST_TITLE, TEST_URL, TEST_DATE_PUBLISHED)
    return test_article

def test_article_init(mock_article: Article) -> None:
    """Test initialization of Article objects"""
    assert mock_article.title == TEST_TITLE
    assert mock_article.url == TEST_URL
    assert mock_article.date_published == TEST_DATE_PUBLISHED

def test_get_pretty_title(mock_article: Article) -> None:
    """Test unescaping of title variable."""
    assert mock_article.get_pretty_title() == TEST_PRETTY_TITLE

def test_get_pretty_date(mock_article: Article) -> None:
    """Test formatting of datetime objects."""
    assert mock_article.get_pretty_date() == TEST_PRETTY_DATE

def test_get_article_from_script_valid_data() -> None:
    """Test data extraction from script tag."""

    # Script with all fields filled.
    test_script_raw = f"""\
    <script>
    {{
        "mainEntityOfPage": {{
            "@type": "WebPage",
            "@id": "{TEST_URL}"
        }},
        "name" : "{TEST_TITLE}",
        "author" : {{
            "name" : "Sarah Salisbury"
        }},
        "datePublished": "{TEST_DATE_PUBLISHED.isoformat()}",
        "dateModified": "2025-04-01T16:03:01-07:00"
    }}
    </script>
    """
    soup = BeautifulSoup(test_script_raw, "html.parser")
    test_script = soup.script

    article = articles._get_article_from_script(test_script)
    assert article.title == TEST_TITLE
    assert article.url == TEST_URL
    assert article.date_published == TEST_DATE_PUBLISHED

def test_get_article_from_script_missing_fields() -> None:
    """Test data extraction from script tag with missing fields."""

    # Script with some fields blank
    test_script_raw = f"""\
    <script>
    {{
        "mainEntityOfPage": {{
            "@type": "WebPage"
        }},
        "name" : "{TEST_TITLE}",
        "author" : {{
            "name" : "Sarah Salisbury"
        }},
        "datePublished": "{TEST_DATE_PUBLISHED.isoformat()}",
        "dateModified": "2025-04-01T16:03:01-07:00"
    }}
    </script>
    """
    soup = BeautifulSoup(test_script_raw, "html.parser")
    test_script = soup.script

    article = articles._get_article_from_script(test_script)

    # Check to make sure the function returns a falsy value.
    assert not article

def test_get_date_published_malformed_data() -> None:
    """Test data extraction from script tag with malformed data."""

    # Script with malformed JSON (commas at the end of dictionaries).
    test_script_raw = f"""\
    <script>
    {{
        "mainEntityOfPage": {{
            "@type": "WebPage",
        }},
        "name" : "{TEST_TITLE}",
        "author" : {{
            "name" : "Sarah Salisbury",
        }},
        "datePublished": "{TEST_DATE_PUBLISHED.isoformat()}",
        "dateModified": "2025-04-01T16:03:01-07:00",
    }}
    </script>
    """
    soup = BeautifulSoup(test_script_raw, "html.parser")
    test_script = soup.script

    with pytest.raises(JSONDecodeError):
        articles._get_article_from_script(test_script)

    # Script with malformed date (incorrect format).
    test_script_raw = f"""\
    <script>
    {{
        "mainEntityOfPage": {{
            "@type": "WebPage"
        }},
        "name" : "{TEST_TITLE}",
        "author" : {{
            "name" : "Sarah Salisbury"
        }},
        "datePublished": "{TEST_PRETTY_DATE}",
        "dateModified": "2025-04-01T16:03:01-07:00"
    }}
    </script>
    """
    soup = BeautifulSoup(test_script_raw, "html.parser")
    test_script = soup.script
    article = articles._get_article_from_script(test_script)

    # The function should return a falsy value in this case
    assert not article

def test_get_date_published_valid_date() -> None:
    """Test script extraction when the date uses a valid format."""

    script_data = {
        "datePublished": TEST_DATE_PUBLISHED.isoformat()
    }
    date_published = articles._get_date_published(script_data)
    assert date_published == TEST_DATE_PUBLISHED

def test_get_date_published_invalid_date() -> None:
    """Test script extraction when the date uses an invalid format."""

    script_data = {
        "datePublished": TEST_PRETTY_DATE
    }

    with pytest.raises(ValueError):
        articles._get_date_published(script_data)

def test_get_articles_from_archive_page_success(monkeypatch: MonkeyPatch) -> None:
    """Test extraction of articles from archive pages."""

    test_html = f"""\
    <html>
    <head></head>
    <body>
        <script>
        {{
            "mainEntityOfPage": {{
                "@type": "WebPage",
                "@id": "{TEST_URL}"
            }},
            "name" : "{TEST_TITLE}",
            "author" : {{
                "name" : "Sarah Salisbury"
            }},
            "datePublished": "{TEST_DATE_PUBLISHED.isoformat()}",
            "dateModified": "2025-04-01T16:03:01-07:00"
        }}
        </script>
        <script>
        {{
            "key": "This script should be filtered."
        }}
        </script>
    </body>
    </html>
    """

    # Class to patch requests.get.
    class MockResponse:
        def __init__(self):
            self.text = test_html

        def raise_for_status(self) -> None:
            pass

    def mock_requests_get(_) -> None:
        return MockResponse()

    monkeypatch.setattr('requests.get', mock_requests_get)

    # Check that the function extracts the single article.
    page_of_articles = articles._get_articles_from_archive_page(1)
    assert len(page_of_articles) == 1

    # Check that the function extracts the proper data.
    article = page_of_articles[0]
    assert article.title == TEST_TITLE
    assert article.url == TEST_URL
    assert article.date_published == TEST_DATE_PUBLISHED

def test_get_article_from_archive_page_404(monkeypatch: MonkeyPatch) -> None:
    """Test response if archive page returns 404."""

    # Class to patch requests.get.
    class MockResponse:
        def raise_for_status(self) -> None:
            response = Response()
            response.status_code = 404
            raise HTTPError(response=response)

    def mock_requests_get(_) -> None:
        return MockResponse()

    monkeypatch.setattr('requests.get', mock_requests_get)

    page_of_articles = articles._get_articles_from_archive_page(1)

    # The function should return a falsy value.
    assert not page_of_articles

def test_get_article_from_archive_page_network_error(monkeypatch: MonkeyPatch) -> None:
    """Test response if unable to connect to archive page."""

    # Class to patch requests.get.
    class MockResponse:
        def raise_for_status(self) -> None:
            raise ConnectionError()

    def mock_requests_get(_) -> None:
        return MockResponse()

    monkeypatch.setattr('requests.get', mock_requests_get)

    with pytest.raises(ConnectionError):
        articles._get_articles_from_archive_page(1)

def test_get_articles_from_archive_page_empty_response(monkeypatch: MonkeyPatch) -> None:
    """Test response if no articles are found."""

    # Class to patch requests.get.
    class MockResponse:
        def __init__(self) -> None:
            self.text = ""

        def raise_for_status(self) -> None:
            pass

    def mock_requests_get(_) -> None:
        return MockResponse()

    monkeypatch.setattr('requests.get', mock_requests_get)

    page_of_articles = articles._get_articles_from_archive_page(1)

    # The function should return a falsy value.
    assert not page_of_articles

def test_get_new_articles_with_new_articles(monkeypatch: MonkeyPatch):
    """Test filtering to ensure new articles are returned."""
    expected_articles_list = [
        Article(TEST_TITLE, TEST_URL, TEST_DATE_PUBLISHED + tdelta(days=1)),
        Article(TEST_TITLE + " 2", TEST_URL, TEST_DATE_PUBLISHED + tdelta(days=2)),
    ]

    # Mock the get_articles function to return a fixed list of articles.
    def mock_get_articles() -> list[Article]:
        return expected_articles_list

    monkeypatch.setattr("cozymeal.articles.get_articles", mock_get_articles)

    articles_list = list(articles.get_new_articles(last_checked=TEST_DATE_PUBLISHED))

    # Check that the length of the two lists is the same.
    # This assures that no duplicates are added in the filtering process.
    assert len(articles_list) == len(expected_articles_list)

    # Check that the two lists have the same elements.
    assert set(articles_list) == set(expected_articles_list)

def test_get_new_articles_with_old_articles(monkeypatch: MonkeyPatch):
    """Test filtering to ensure old articles are filtered."""
    expected_articles_list = [
        Article(TEST_TITLE, TEST_URL, TEST_DATE_PUBLISHED - tdelta(days=1)),
        Article(TEST_TITLE + " 2", TEST_URL, TEST_DATE_PUBLISHED - tdelta(days=2)),
    ]

    # Mock the get_articles function to return a fixed list of articles.
    def mock_get_articles() -> list[Article]:
        return expected_articles_list

    monkeypatch.setattr("cozymeal.articles.get_articles", mock_get_articles)

    articles_list = list(articles.get_new_articles(last_checked=TEST_DATE_PUBLISHED))

    # Check that the function returns an empty list.
    assert len(articles_list) == 0

def test_get_new_articles_empty_list(monkeypatch: MonkeyPatch):
    """Test filtering with an empty list."""
    # Mock the get_articles function to return a fixed list of articles.
    def mock_get_articles() -> list[Article]:
        return []

    monkeypatch.setattr("cozymeal.articles.get_articles", mock_get_articles)

    articles_list = list(articles.get_new_articles(last_checked=TEST_DATE_PUBLISHED))

    # Check that the function returns an empty list.
    assert len(articles_list) == 0

def test_get_new_articles_sorting_order(monkeypatch: MonkeyPatch):
    """Test that filtering returns the articles in reverse date order."""
    expected_articles_list = [
        Article(TEST_TITLE, TEST_URL, TEST_DATE_PUBLISHED + tdelta(days=1)),
        Article(TEST_TITLE + " 2", TEST_URL, TEST_DATE_PUBLISHED + tdelta(days=2)),
    ]

    # Mock the get_articles function to return a fixed list of articles.
    def mock_get_articles() -> list[Article]:
        return expected_articles_list

    monkeypatch.setattr("cozymeal.articles.get_articles", mock_get_articles)

    articles_list: list[Article] = list(articles.get_new_articles(last_checked=TEST_DATE_PUBLISHED))

    # Check that the articles are sorted in reverse date order.
    assert articles_list[0].date_published > articles_list[1].date_published
