from setuptools import find_packages, setup

from pomodoro import __version__, __homepage__

setup(
    name="django-pomodoro",
    description="Render Pomodoro Calendars",
    author="Paul Traylor",
    url=__homepage__,
    version=__version__,
    packages=find_packages(),
    install_requires=[
        "Django>=2.1",
        "djangorestframework",
        "icalendar",
        "Pillow",
        "python-dateutil",
        "requests",
    ],
    extras_require={
        "standalone": [
            "celery==4.3.0",
            "django-environ",
            "paho-mqtt",
            "sentry_sdk",
        ],
        "dev": [
            "black",
            "django_nose",
            "psycopg2-binary",
            "unittest-xml-reporting",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Django",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    entry_points={
        "pomodoro.notification": [
            "line = pomodoro.notifications.line:Line",
            "prowl = pomodoro.notifications.prowl:Prowl",
            "mqtt = pomodoro.notifications.mqtt:MQTT",
        ],
        "console_scripts": ["pomodoro = pomodoro.standalone.manage:main[standalone]"],
    },
)
