import os
import envdir

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pomodoro.standalone.settings")
os.environ.setdefault("ENVDIR", os.path.expanduser("~/.config/pomodoro"))

if os.path.exists(os.environ["ENVDIR"]):
    envdir.open(os.environ["ENVDIR"])

# Preload Celery App
from pomodoro.standalone.celery import app as celery_app  # noqa
