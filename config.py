"""All settings come from environment variables, so nothing secret lives in the code or image."""
import os

MYSQL_HOST = os.getenv("MYSQL_HOST", "db")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER", "app")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "bookshelf")
CONNECT_TIMEOUT = int(os.getenv("CONNECT_TIMEOUT", "5"))

# Set to the git commit SHA by the CI pipeline at build time
APP_VERSION = os.getenv("APP_VERSION", "dev")
