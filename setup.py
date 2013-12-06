#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='django-pomodoro',
    description='Render Pomodoro Calendars',
    author='Paul Traylor',
    url='https://github.com/kfdm/django-pomodoro',
    version='0.0.1',
    packages=['pomodoro'],
    install_requires=['icalendar'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)
