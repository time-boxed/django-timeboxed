

from pomodoro.models import Favorite, Pomodoro, Tag

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class ApiTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="Test User", password="")
        self.client.force_login(self.user)

    def test_start_from_favorite(self):
        favorite = Favorite.objects.create(title="Test", duration=5, owner=self.user)

        response = self.client.post(reverse("api:favorite-start", args=[favorite.pk]))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Favorite.objects.count(), 1)

    def test_create_pomodoro(self):
        response = self.client.post(
            reverse("api:pomodoro-list"),
            data={"title": "foo", "tags": ["a", "b"]},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Pomodoro.objects.count(), 1)
        self.assertEqual(Tag.objects.count(), 2)
