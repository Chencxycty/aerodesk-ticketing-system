import os

import psycopg2
from dotenv import load_dotenv


load_dotenv()


ROLE_CREDENTIALS = {
    "passenger": ("DB_PASSENGER_USER", "DB_PASSENGER_PASSWORD"),
    "admin": ("DB_ADMIN_USER", "DB_ADMIN_PASSWORD"),
    "company": ("DB_COMPANY_USER", "DB_COMPANY_PASSWORD"),
}


def connect_db(role):
    """Create a database connection for one of the application's roles."""
    if role not in ROLE_CREDENTIALS:
        raise ValueError("Unsupported database role: %s" % role)

    user_key, password_key = ROLE_CREDENTIALS[role]
    config = {
        "database": os.getenv("DB_NAME", "dbflight_ticket_book"),
        "user": os.getenv(user_key),
        "password": os.getenv(password_key),
        "host": os.getenv("DB_HOST", "127.0.0.1"),
        "port": os.getenv("DB_PORT", "5432"),
    }
    missing = [key for key in (user_key, password_key) if not os.getenv(key)]
    if missing:
        raise RuntimeError(
            "Missing database configuration: %s. Copy .env.example to .env and fill it in."
            % ", ".join(missing)
        )

    return psycopg2.connect(**config)
