"""Integration tests: talk to a real MySQL database.

They run in CI (MySQL service container) and in `docker compose --profile test run test-runner`.
Locally, without MYSQL_HOST set, they are skipped.
"""
import os

import pytest

from app import app

pytestmark = pytest.mark.skipif(not os.getenv("MYSQL_HOST"), reason="needs a MySQL database (set MYSQL_HOST)")


@pytest.fixture
def client():
    app.testing = True
    return app.test_client()


def test_ready_when_database_is_up(client):
    res = client.get("/ready")
    assert res.status_code == 200
    assert res.get_json()["database"] == "connected"


def test_seed_data_is_loaded(client):
    books = client.get("/api/books").get_json()
    assert len(books) >= 5
    assert "The Phoenix Project" in [b["title"] for b in books]


def test_add_book_and_read_it_back(client):
    res = client.post("/api/books", json={"title": "Team Topologies", "author": "Matthew Skelton", "year": 2019})
    assert res.status_code == 201
    new_id = res.get_json()["id"]

    books = client.get("/api/books").get_json()
    assert any(b["id"] == new_id and b["title"] == "Team Topologies" for b in books)


def test_stats_counts_books_and_authors(client):
    stats = client.get("/api/stats").get_json()
    assert stats["books"] >= 5
    assert stats["authors"] >= 4
    assert stats["oldest_year"] <= 2010