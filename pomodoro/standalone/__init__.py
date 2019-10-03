import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pomodoro.standalone.settings")
os.environ.setdefault("DJANGO_ENV_FILE", ".env")

from . import celery  # NOQA
