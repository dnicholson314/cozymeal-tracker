import pytest

from app import app as flask_app
from contextlib import contextmanager
from datetime import datetime as dt
from flask import Flask, template_rendered
from flask.testing import FlaskClient
from pytest import MonkeyPatch
from typing import Any, Generator
from cozymeal import settings

VALID_TOKEN = 'valid_token'
INITIAL_TIME = dt(2023, 1, 1, tzinfo=settings.DEFAULT_TZ)

@pytest.fixture
def mock_cozymeal(monkeypatch: MonkeyPatch) -> None:
    """Set up common mocking behavior for cozymeal tests."""

    monkeypatch.setattr('cozymeal.settings.API_TOKEN', VALID_TOKEN)
    monkeypatch.setattr('cozymeal.articles.get_new_articles', lambda _: ["spoof_article"])
    monkeypatch.setattr('cozymeal.emails.send_email_for_articles', lambda _: None)
    monkeypatch.setattr('cozymeal.utils.get_last_checked', lambda: INITIAL_TIME)
    monkeypatch.setattr('cozymeal.utils.set_last_checked', lambda _: None)

@contextmanager
def captured_templates(app: Flask):
    """Context manager to capture templates rendered during a request."""

    recorded = []

    def record(sender, template, context, **extra):
        recorded.append((template, context))

    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)

@pytest.fixture
def app() -> Generator[Flask, Any, None]:
    """Create and configure a Flask app for testing."""

    flask_app.config.update({
        "TESTING": True,
    })
    yield flask_app

@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """Create a test client for the app."""

    return app.test_client()

def test_home_page(client: FlaskClient, app: Flask) -> None:
    """Test that the home page loads successfully and renders the correct template."""

    with captured_templates(app) as templates:
        response = client.get('/')

        # Check if status code is 200 (OK)
        assert response.status_code == 200

        # Check if the correct template was rendered
        assert len(templates) == 1
        template, context = templates[0]
        assert template.name == 'home.html'

        # Additional checks for expected context variables
        assert 'last_checked' in context

def test_post_without_auth(client: FlaskClient) -> None:
    """Test POST request with no credentials."""

    response = client.post("/")

    assert response.status_code == 401

def test_post_with_malformed_auth(client: FlaskClient) -> None:
    """Test POST request with malformed credentials."""

    headers = {
        "Authorization": "malformed credentials"
    }
    response = client.post("/", headers=headers)

    assert response.status_code == 401

def test_post_with_invalid_auth(client: FlaskClient, mock_cozymeal, monkeypatch: MonkeyPatch) -> None:
    """Test POST request with invalid credentials. Also check that last_checked isn't updated."""

    updated_time = False

    # Mock function to track if set_last_checked was called
    def mock_set_last_checked(_):
        nonlocal updated_time
        updated_time = True

    monkeypatch.setattr('cozymeal.utils.set_last_checked', mock_set_last_checked)

    # Make POST request with incorrect token
    headers = {
        "Authorization": "Bearer invalid_token"
    }
    response = client.post("/", headers=headers)

    # Verify response failed and last_checked wasn't updated
    assert response.status_code == 401
    assert updated_time is False

def test_post_with_valid_auth(client: FlaskClient, mock_cozymeal, monkeypatch: MonkeyPatch) -> None:
    """Test POST request with valid credentials and new articles. Also check that last_checked is updated."""

    updated_time = False

    # Mock function to track if set_last_checked was called with a newer timestamp
    def mock_set_last_checked(timestamp: dt) -> bool:
        nonlocal updated_time
        assert timestamp > INITIAL_TIME
        updated_time = True

    # Override only the set_last_checked function
    monkeypatch.setattr('cozymeal.utils.set_last_checked', mock_set_last_checked)

    # Make POST request with valid authentication
    headers = {
        "Authorization": f"Bearer {VALID_TOKEN}"
    }
    response = client.post("/", headers=headers)

    # Verify response and that last_checked was updated
    assert response.status_code == 200
    assert updated_time is True

def test_post_with_valid_auth_no_articles(client: FlaskClient, mock_cozymeal, monkeypatch: MonkeyPatch) -> None:
    """Test POST request with valid credentials but no new articles. Also check that last_checked isn't updated."""

    updated_time = False

    def mock_set_last_checked(timestamp: dt) -> bool:
        nonlocal updated_time
        assert timestamp > INITIAL_TIME
        updated_time = True

    # Override the default mock to return empty articles list
    monkeypatch.setattr('cozymeal.articles.get_new_articles', lambda _: [])
    monkeypatch.setattr('cozymeal.utils.set_last_checked', mock_set_last_checked)

    headers = {
        "Authorization": f"Bearer {VALID_TOKEN}"
    }
    response = client.post("/", headers=headers)

    assert response.status_code == 204
    assert updated_time is False

def test_last_checked_none(client: FlaskClient, mock_cozymeal, monkeypatch: MonkeyPatch) -> None:
    """Test POST request with valid credentials but no previous last_checked value."""

    def mock_get_new_articles(last_checked: dt) -> list:
        assert last_checked == INITIAL_TIME
        return ["spoof_article"]

    monkeypatch.setattr('cozymeal.utils.get_last_checked', lambda: None)
    monkeypatch.setattr('cozymeal.utils.get_date_a_week_ago', lambda: INITIAL_TIME)
    monkeypatch.setattr('cozymeal.articles.get_new_articles', mock_get_new_articles)

    headers = {
        "Authorization": f"Bearer {VALID_TOKEN}"
    }
    response = client.post("/", headers=headers)

    assert response.status_code == 200