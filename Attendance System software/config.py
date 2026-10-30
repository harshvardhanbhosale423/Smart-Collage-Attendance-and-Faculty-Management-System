import os
import sys
from datetime import timedelta
from dotenv import load_dotenv

if getattr(sys, "frozen", False):
    # Running as a packaged .exe: bundled files (templates/static) live in
    # BASE_DIR, but the database/backups/.env must live NEXT TO the .exe so
    # they survive restarts.
    BASE_DIR = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    DATA_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATA_DIR = BASE_DIR

load_dotenv(os.path.join(DATA_DIR, ".env"))


def _bool(val, default=False):
    if val is None:
        return default
    return str(val).strip().lower() in ("1", "true", "yes", "on")


class Config:
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-only-change-me")
    DEBUG = _bool(os.environ.get("FLASK_DEBUG"), False)

    # Defaults to sqlite so the app works immediately with zero setup.
    # For real college LAN deployment, set DB_ENGINE=mysql in .env and
    # configure MariaDB (see README section 4.2).
    # For live internet deployment (e.g. Render/Railway/Heroku), those
    # platforms usually inject a DATABASE_URL env var automatically when
    # you attach a PostgreSQL database - that takes priority over everything
    # else below if present.
    _database_url = os.environ.get("DATABASE_URL")
    DB_ENGINE = os.environ.get("DB_ENGINE", "sqlite").lower()

    if _database_url:
        # Render/Heroku-style URLs sometimes start with postgres:// - modern
        # SQLAlchemy requires postgresql://
        if _database_url.startswith("postgres://"):
            _database_url = _database_url.replace("postgres://", "postgresql://", 1)
        SQLALCHEMY_DATABASE_URI = _database_url
    elif DB_ENGINE == "sqlite":
        SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(DATA_DIR, "database", "attendance.db")
    else:
        DB_USER = os.environ.get("DB_USER", "attendance_user")
        DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
        DB_HOST = os.environ.get("DB_HOST", "localhost")
        DB_PORT = os.environ.get("DB_PORT", "3306")
        DB_NAME = os.environ.get("DB_NAME", "attendance_system")
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    PERMANENT_SESSION_LIFETIME = timedelta(
        minutes=int(os.environ.get("SESSION_LIFETIME_MINUTES", 60))
    )
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    WTF_CSRF_ENABLED = True

    DEFAULT_WARNING_THRESHOLD = float(os.environ.get("ATTENDANCE_WARNING_THRESHOLD", 75))
    DEFAULT_CRITICAL_THRESHOLD = float(os.environ.get("ATTENDANCE_CRITICAL_THRESHOLD", 65))

    BACKUP_DIR = os.path.join(DATA_DIR, "backups")
    REPORTS_DIR = os.path.join(DATA_DIR, "reports")
