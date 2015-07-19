import datetime

import pytz
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db.backends.sqlite3.base import DatabaseWrapper
from pomodoro.legacy import NSTIMEINTERVAL
from pomodoro.models import Pomodoro


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('user')
        parser.add_argument('inputfile')

    def handle(self, *args, **options):
        user = User.objects.get(username=options['user'])
        pomodoros = Pomodoro.objects.filter(owner=user)
        while len(pomodoros):
            print 'Delete ', len(pomodoros), 'pomodoros for', user, '?'
            if raw_input('Confirm yes/no ').lower() == 'yes':
                break
        pomodoros.delete()
        print 'Importing Pomodoros'

        cursor = DatabaseWrapper(settings_dict={
            'NAME': options['inputfile'],
            'CONN_MAX_AGE': None,
            'OPTIONS': [],
            'AUTOCOMMIT': False,
        }).cursor()
        cursor.execute('SELECT cast(ZWHEN as integer), ZDURATIONMINUTES, ZNAME FROM ZPOMODOROS ')
        for zwhen, zminutes, zname in cursor.fetchall():
            seconds = zminutes * 60

            p = Pomodoro()
            p.title = zname
            p.owner = user
            #  p.start = datetime.datetime.fromtimestamp(zwhen + NSTIMEINTERVAL - seconds, pytz.utc)
            #  p.end = datetime.datetime.fromtimestamp(zwhen + NSTIMEINTERVAL, pytz.utc)
            p.created = datetime.datetime.fromtimestamp(zwhen + NSTIMEINTERVAL - seconds, pytz.utc)
            p.duration = zminutes
            p.save()
            print 'Added', p
