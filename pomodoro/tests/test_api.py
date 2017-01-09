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
        duration = 1337
        now = datetime.datetime.utcnow()

        response = self.client.post(
            reverse('api:pomodoro-append'),
            data={
                'created': (now - datetime.timedelta(minutes=duration)).strftime(self.timeformat),
                'category': 'tags',
                'duration': duration,
                'title': 'title',
            },
        )
        self.assertEqual(response.status_code, 201)
        pomodoro = Pomodoro.objects.get()
        self.assertEquals(pomodoro.duration, 1337)

    def test_double_append(self):
        duration = 1337
        second = datetime.datetime.utcnow().replace(microsecond=0)
        first = second - datetime.timedelta(minutes=duration)

        response = self.client.post(
            reverse('api:pomodoro-append'),
            data={
                'created': first.strftime(self.timeformat),
                'category': 'tags',
                'duration': duration,
                'title': 'title',
            },
        )
        self.assertEqual(response.status_code, 201, 'First pomodoro created')
        pomodoro = Pomodoro.objects.get()
        self.assertEquals(pomodoro.duration, 1337)

        response = self.client.post(
            reverse('api:pomodoro-append'),
            data={
                'created': second.strftime(self.timeformat),
                'category': 'tags',
                'duration': 1,
                'title': 'title',
            },
        )

        self.assertEqual(response.status_code, 200, 'Appended to Pomodoro')
        pomodoro = Pomodoro.objects.get()
        self.assertEquals(pomodoro.duration, 1338)
