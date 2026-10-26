import pymysql
from flask import Flask, jsonify, render_template, request

import config

app = Flask(__name__)


def get_connection():
    return pymysql.connect(
        host=config.MYSQL_HOST,
        port=config.MYSQL_PORT,
        user=config.MYSQL_USER,
        password=config.MYSQL_PASSWORD,
        database=config.MYSQL_DATABASE,
        connect_timeout=config.CONNECT_TIMEOUT,
        cursorclass=pymysql.cursors.DictCursor,
    )


def validate_book(data):
    """Return a list of validation errors for a new book (empty list = valid)."""
    errors = []
    if not str(data.get("title", "")).strip():
        errors.append("title is required")
    if not str(data.get("author", "")).strip():
        errors.append("author is required")
    year = data.get("year")
    if year not in (None, ""):
        try:
            if not 1000 <= int(year) <= 2100:
                errors.append("year must be between 1000 and 2100")
        except (TypeError, ValueError):
            errors.append("year must be a number")
    return errors


def fetch_books():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, title, author, year FROM books ORDER BY id")
            return cur.fetchall()
    finally:
        conn.close()


@app.route("/")
def index():
    try:
        books, error = fetch_books(), None
    except pymysql.MySQLError:
        books, error = [], "Database is unavailable"
    return render_template("index.html", books=books, error=error, version=config.APP_VERSION)


@app.route("/health")
def health():
    """Liveness: the app process is up (used by Docker HEALTHCHECK)."""
    return jsonify(status="ok", version=config.APP_VERSION)


@app.route("/ready")
def ready():
    """Readiness: the app can reach its database."""
    try:
        conn = get_connection()
        conn.ping()
        conn.close()
        return jsonify(status="ready", database="connected")
    except pymysql.MySQLError:
        return jsonify(status="not ready", database="unreachable"), 503


@app.route("/api/books", methods=["GET"])
def list_books():
    try:
        return jsonify(fetch_books())
    except pymysql.MySQLError:
        return jsonify(error="Database is unavailable"), 503


@app.route("/api/books", methods=["POST"])
def add_book():
    data = request.get_json(silent=True) or {}
    errors = validate_book(data)
    if errors:
        return jsonify(errors=errors), 400

    title, author = str(data["title"]).strip(), str(data["author"]).strip()
    year = int(data["year"]) if data.get("year") not in (None, "") else None
    try:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO books (title, author, year) VALUES (%s, %s, %s)", (title, author, year))
                book_id = cur.lastrowid
            conn.commit()
        finally:
            conn.close()
    except pymysql.MySQLError:
        return jsonify(error="Database is unavailable"), 503

    return jsonify(id=book_id, title=title, author=author, year=year), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
