import os
import envdir

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pomodoro.standalone.settings")

CONFIG_DIR = os.path.expanduser('~/.config/pomodoro')

if os.path.exists(CONFIG_DIR):
    envdir.open(CONFIG_DIR)
