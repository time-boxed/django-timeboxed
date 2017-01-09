import datetime

from rest_framework.authtoken.models import Token

from pomodoro.models import Pomodoro

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse


class ApiTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='Test User', password='')
        self.token = Token.objects.create(user=self.user)
        self.client = Client(**{'HTTP_AUTHORIZATION': 'Token %s' % self.token})
        self.timeformat = '%Y-%m-%dT%H:%M:%SZ'

    def test_single_append(self):
        duration =  datetime.timedelta(minutes=1337)
        end = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)
        start = end - duration

        response = self.client.post(
            reverse('api:pomodoro-append'),
            data={
                'start': start.strftime(self.timeformat),
                'end': end.strftime(self.timeformat),
                'category': 'tags',
                'title': 'title',
            },
        )
        self.assertEqual(response.status_code, 201)
        pomodoro = Pomodoro.objects.get()
        self.assertEquals(pomodoro.duration, duration, 'Duration mismatch')

    def test_double_append(self):
        duration = datetime.timedelta(minutes=1337)
        appended = datetime.timedelta(minutes=1338)

        middle = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)
        start = middle - duration
        end = middle + datetime.timedelta(minutes=1)

        response = self.client.post(
            reverse('api:pomodoro-append'),
            data={
                'start': start.strftime(self.timeformat),
                'end': middle.strftime(self.timeformat),
                'category': 'tags',
                'title': 'title',
            },
        )
        self.assertEqual(response.status_code, 201, 'First pomodoro created')
        pomodoro = Pomodoro.objects.get()
        self.assertEquals(pomodoro.duration, duration)

        response = self.client.post(
            reverse('api:pomodoro-append'),
            data={
                'start': middle.strftime(self.timeformat),
                'end': end.strftime(self.timeformat),
                'category': 'tags',
                'title': 'title',
            },
        )

        self.assertEqual(response.status_code, 200, 'Appended to Pomodoro')
        pomodoro = Pomodoro.objects.get()
        self.assertEquals(pomodoro.duration, appended, 'Duration mismatch')
        self.assertEquals(pomodoro.start, start, 'Start mismatch')
        self.assertEquals(pomodoro.end, end, 'End mismatch')
