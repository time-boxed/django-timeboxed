from setuptools import find_packages, setup

from pomodoro import __version__, __homepage__

setup(
    name='django-pomodoro',
    description='Render Pomodoro Calendars',
    author='Paul Traylor',
    url=__homepage__,
    version=__version__,
    packages=find_packages(),
    install_requires=[
        "Django>=2.1",
        "djangorestframework",
        "icalendar",
        "Pillow",
        "requests",
    ],
    extras_require={
        "standalone": [
            'pillow==6.1.0',
            "celery==4.3.0",
            "django-environ",
            "Django==2.2.5",
            "djangorestframework==3.10.3",
            "paho-mqtt",
            "prometheus_client==0.7.1",
            "redis>=2.10.5",
            "requests==2.22.0",
            "sentry_sdk",
            "social-auth-app-django==2.1.0",
        ],
        'dev': [
            'unittest-xml-reporting',
        ]
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    entry_points={
        'powerplug.apps': ['pomodoro = pomodoro.apps.PomodoroConfig'],
        'powerplug.urls': ['pomodoro = pomodoro.urls'],
        'powerplug.rest': [
            'pomodoro = pomodoro.rest:PomodoroViewSet',
            'favorite = pomodoro.rest:FavoriteViewSet',
        ],
        'console_scripts': [
            'pomodoro = pomodoro.standalone.manage:main[standalone]',
        ],
    },
)
