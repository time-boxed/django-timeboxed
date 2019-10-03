from pomodoro.models import Favorite

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse


class ApiTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="Test User", password="")
        self.client.force_login(self.user)

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_query(self):
        favorite = Favorite.objects.create(title="Test", duration=5, owner=self.user)

        response = self.client.post(reverse("api:favorite-start", args=[favorite.pk]))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Favorite.objects.count(), 1)
