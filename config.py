import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")

    #  SQLite REMOVED — PostgreSQL REQUIRED
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")

    if not SQLALCHEMY_DATABASE_URI:
        raise RuntimeError(
            " DATABASE_URL is not set. PostgreSQL is REQUIRED."
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True

    # Flask-Login
    REMEMBER_COOKIE_DURATION = 60 * 60 * 24 * 14  # 14 days


class DevConfig(Config):
    DEBUG = True


class ProdConfig(Config):
    DEBUG = False









# import os

# class Config:
#     SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
#     # Default to SQLite for quick start; override with MySQL via env vars
#     SQLALCHEMY_DATABASE_URI = os.environ.get(
#         "DATABASE_URL",
#         "sqlite:///app.db"
#     )
#     SQLALCHEMY_TRACK_MODIFICATIONS = False
#     WTF_CSRF_ENABLED = True

#     # Flask-Login
#     REMEMBER_COOKIE_DURATION = 60 * 60 * 24 * 14  # 14 days

# class ProdConfig(Config):
#     DEBUG = False

# class DevConfig(Config):
#     DEBUG = True
