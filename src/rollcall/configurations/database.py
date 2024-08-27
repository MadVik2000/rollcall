from os import environ


def get_database_config():
    return {
        "default": {
            "ENGINE": "django.db.backends.postgresql_psycopg2",
            "NAME": environ["DATABASE_NAME"],
            "USER": environ["DATABASE_USERNAME"],
            "PASSWORD": environ["DATABASE_PASSWORD"],
            "HOST": environ["DATABASE_HOST"],
            "PORT": environ["DATABASE_PORT"],
        }
    }
