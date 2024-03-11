import datetime
import os
import random


def _upload_to_path(instance, filename):
    _, ext = os.path.splitext(filename)
    return f"pomodoro/favorites/{instance.pk}{ext}"


def color():
    return "%06x" % random.randint(0, 0xFFFFFF)


def to_ts(dt):
    return dt.timestamp() * 1000


def floor(dt):
    return datetime.datetime.combine(dt, datetime.time.min, tzinfo=dt.tzinfo)
