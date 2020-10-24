from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class ApiTest(TestCase):
    fixtures = ["test.json"]

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.client.force_login(self.user)

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
