from pomodoro.models import Favorite, Pomodoro

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse


class ApiTest(TestCase):
    fixtures = ["test.json"]

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.client.force_login(self.user)

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_start_favorite(self):
        response = self.client.post(reverse("api:favorite-start", args=[1]))
        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(Favorite.objects.count(), 1)

    def test_create_pomodoro(self):
        """Test creating pomodoro with just project id"""
        response = self.client.post(
            reverse("api:pomodoro-list"),
            content_type="application/json",
            data={
                "title": "Test with project_id",
                "project": "07f03c60-9b2c-4ee5-ad2f-c5e2eaa213f4",
            },
        )
        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(
            Pomodoro.objects.count(), 2, "Created pomodoro with project id"
        )

    def test_create_pomodoro_nested(self):
        """Test creating pomodoro with nested project"""

        response = self.client.post(
            reverse("api:pomodoro-list"),
            content_type="application/json",
            data={
                "title": "Test with nested project",
                "project": {"id": "07f03c60-9b2c-4ee5-ad2f-c5e2eaa213f4"},
            },
        )
        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(
            Pomodoro.objects.count(), 2, "Created a pomodoro with nested project"
        )

    def test_create_pomodoro_no_project(self):
        """Test creating pomodoro without project"""

        response = self.client.post(
            reverse("api:pomodoro-list"),
            content_type="application/json",
            data={"title": "Test without project",},
        )
        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(
            Pomodoro.objects.count(), 2, "Created a pomodoro without project"
        )

    def test_remove_project(self):
        response = self.client.put(
            reverse("api:pomodoro-detail", kwargs={"pk": 1}),
            content_type="application/json",
            data={"title": "Test update without project"},
        )
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(Pomodoro.objects.count(), 1, "Updated and removed Project")

    def test_change_project(self):
        response = self.client.put(
            reverse("api:pomodoro-detail", kwargs={"pk": 1}),
            content_type="application/json",
            data={
                "title": "Test change project",
                "project": "1b33e4ff-87f8-4bca-bc44-5264e2a5ffb1",
            },
        )
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(
            Pomodoro.objects.count(), 1, "Changed the project of an existing pomodoro"
        )

