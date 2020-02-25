from pomodoro.models import Favorite

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse


class ApiTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="Test User", password="")
        self.client.force_login(self.user)

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_start_favorite(self):
        favorite = Favorite.objects.create(title="Test", duration=5, owner=self.user)

        response = self.client.post(reverse("api:favorite-start", args=[favorite.pk]))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Favorite.objects.count(), 1)

    def test_grafana_query(self):
        # https://github.com/grafana/simple-json-datasource#query-api
        # TODO: Add actual data to test query
        response = self.client.post(
            reverse("grafana:query"),
            content_type="application/json",
            data={
                "range": {"from": "2020-01-01T00:00:00Z", "to": "2020-02-02T00:00:00Z"},
                "targets": [{"target": "A"}],
            },
        )
        self.assertEqual(response.status_code, 200)
