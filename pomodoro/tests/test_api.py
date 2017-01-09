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

    def test_single_append(self):
        now = datetime.datetime.utcnow()
        duration = 1

        response = self.client.post(
            reverse('api:pomodoro-append'),
            data={
                'start': (now - datetime.timedelta(minutes=duration)).isoformat(),
                'category': ['tags'],
                'duration': duration,
                'title': 'title',
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEquals(Pomodoro.objects.count(), 1)
