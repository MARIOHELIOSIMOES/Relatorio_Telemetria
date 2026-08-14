import keyring


# ==========================================
# PostgreSQL
# ==========================================

pg_host = keyring.get_password(
    "POSTGRES_HOST",
    "host"
)

pg_port = keyring.get_password(
    "POSTGRES_HOST",
    "porta"
)

pg_database = keyring.get_password(
    "POSTGRES_DB_TELEMETRIA",
    "database"
)

pg_user = keyring.get_password(
    "POSTGRES_USER_TELEMETRIA",
    "usuario"
)

pg_password = keyring.get_password(
    "POSTGRES_USER_TELEMETRIA",
    "senha"
)


# ==========================================
# Flask
# ==========================================

SECRET_KEY = keyring.get_password(
    "FLASK_SECRET",
    "secret"
)


# ==========================================
# SQLAlchemy
# ==========================================

SQLALCHEMY_DATABASE_URI = (
    f"postgresql+psycopg2://"
    f"{pg_user}:{pg_password}"
    f"@{pg_host}:{pg_port}"
    f"/{pg_database}"
)

SQLALCHEMY_TRACK_MODIFICATIONS = False