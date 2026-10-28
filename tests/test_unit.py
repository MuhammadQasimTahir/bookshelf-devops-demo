"""Unit tests: no database needed. The DB is replaced with a fake that always fails."""
import pymysql
import pytest

import app as app_module
from app import app, validate_book


@pytest.fixture
def client():
    app.testing = True
    return app.test_client()


@pytest.fixture
def db_down(monkeypatch):
    def fail():
        raise pymysql.err.OperationalError(2003, "Can't connect to MySQL server")

    monkeypatch.setattr(app_module, "get_connection", fail)


def test_valid_book_has_no_errors():
    assert validate_book({"title": "Accelerate", "author": "Nicole Forsgren", "year": 2018}) == []


def test_title_and_author_are_required():
    assert validate_book({}) == ["title is required", "author is required"]


@pytest.mark.parametrize("year", ["abc", 99, 3000])
def test_bad_year_is_rejected(year):
    assert len(validate_book({"title": "X", "author": "Y", "year": year})) == 1


def test_health_works_without_database(client, db_down):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.get_json()["status"] == "ok"


def test_ready_reports_503_when_database_is_down(client, db_down):
    assert client.get("/ready").status_code == 503


def test_homepage_handles_database_error(client, db_down):
    res = client.get("/")
    assert res.status_code == 200
    assert b"Bookshelf" in res.data
    assert b"Database is unavailable" in res.data


def test_invalid_book_returns_400_before_touching_db(client, db_down):
    res = client.post("/api/books", json={"title": ""})
    assert res.status_code == 400


def test_homepage_shows_book_count(client, monkeypatch):
    fake_books = [
        {"id": 1, "title": "Accelerate", "author": "Nicole Forsgren", "year": 2018},
        {"id": 2, "title": "The Phoenix Project", "author": "Gene Kim", "year": 2013},
    ]
    monkeypatch.setattr(app_module, "fetch_books", lambda: fake_books)
    res = client.get("/")
    assert b"2 books on the shelf" in res.data


def test_stats_returns_503_when_database_is_down(client, db_down):
    assert client.get("/api/stats").status_code == 503

 
def test_search_filters_books(client, monkeypatch):
    fake_books = [
        {"id": 1, "title": "Accelerate", "author": "Nicole Forsgren", "year": 2018},
        {"id": 2, "title": "The Phoenix Project", "author": "Gene Kim", "year": 2013},
    ]
    monkeypatch.setattr(app_module, "fetch_books", lambda: fake_books)
    res = client.get("/?q=PHOENIX")
    assert b"The Phoenix Project" in res.data
    assert b"Accelerate" not in res.data    
