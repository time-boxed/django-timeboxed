from setuptools import find_packages, setup

from pomodoro import __version__, __homepage__

setup(
    name='django-pomodoro',
    description='Render Pomodoro Calendars',
    author='Paul Traylor',
    url=__homepage__,
    version=__version__,
    packages=find_packages(),
    install_requires=['icalendar', 'Pillow'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    entry_points={
        'powerplug.apps': ['pomodoro = pomodoro'],
        'powerplug.urls': ['pomodoro = pomodoro.urls'],
        'powerplug.rest': [
            'pomodoro = pomodoro.rest:PomodoroViewSet',
            'favorite = pomodoro.rest:FavoriteViewSet',
        ],
        'powerplug.subnav': ['pomodoro = pomodoro.urls:subnav'],
    },
)
