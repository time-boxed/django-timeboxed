from setuptools import find_packages, setup

from pomodoro import __homepage__, __version__

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
        "requests==2.20.1",
    ],
    extras_require={
        "standalone": [
            "celery==4.2.1",
            "dj_database_url",
            "envdir",
            "paho-mqtt",
            "prometheus_client",
            "redis>=2.10.5",
            "sentry_sdk",
            "social-auth-app-django==2.1.0",
        ],
        "dev": ["codecov", "django-nose", "factory_boy", "nose-cov"],
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
        "powerplug.apps": ["pomodoro = pomodoro.apps.PomodoroConfig"],
        "powerplug.urls": ["pomodoro = pomodoro.urls"],
        "powerplug.rest": [
            "pomodoro = pomodoro.rest:PomodoroViewSet",
            "favorite = pomodoro.rest:FavoriteViewSet",
        ],
        "console_scripts": ["pomodoro = pomodoro.standalone.manage:main[standalone]"],
    },
)
