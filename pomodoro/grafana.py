import collections
import json
import logging

from dateutil.parser import parse
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from . import models

from django.http import JsonResponse
from django.urls import path
from django.views.generic.base import TemplateView

logger = logging.getLogger(__name__)

NOCATEGORY = "{Uncategorized}"


class Help(TemplateView):

    template_name = "pomodoro/grafana/help.html"


class Search(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    def post(self, request, **kwargs):
        query = json.loads(request.body.decode("utf8"))
        logger.debug("search %s", query)
        categories = (
            models.Pomodoro.objects.filter(owner=self.request.user)
            .exclude(category="")
            .order_by("category")
            .values_list("category", flat=True)
            .distinct("category")
        )
        return JsonResponse([NOCATEGORY] + list(categories), safe=False)


def to_ts(dt):
    return dt.timestamp() * 1000


class Query(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    def datapoints(self, targets, start, end):
        durations = collections.defaultdict(lambda: collections.defaultdict(int))
        for name, date, duration in self.fetch(targets, start, end):
            durations[date][name] += duration
        for date in durations:
            for name in durations[date]:
                key = date
                value = durations[date][name]
                yield {"target": name, "datapoints": [key, value]}

    def targets(self, targets, start, end):
        for t in targets:
            _search = "" if t["target"] == NOCATEGORY else t["target"]

            for pomodoro in (
                models.Pomodoro.objects.filter(owner=self.request.user)
                .filter(category=_search)
                .filter(start__gte=start)
                .filter(end__lte=end)
            ):

                midnight = pomodoro.end.replace(
                    hour=0, minute=0, second=0, microsecond=0
                )

                if pomodoro.start.date() == pomodoro.end.date():
                    yield pomodoro.name, pomodoro.start.date(), pomodoro.end - pomodoro.start
                else:
                    yield pomodoro.name, pomodoro.start.date(), midnight - pomodoro.start
                    yield pomodoro.name, pomodoro.start.date(), pomodoro.end - mindnight

    def post(self, request, **kwargs):
        print(request)
        query = json.loads(request.body.decode("utf8"))
        start = parse(query["range"]["from"])
        end = parse(query["range"]["to"])

        logger.debug("%s %s %s", query, start, end)

        return JsonResponse(
            list(self.datapoints(query["targets"], start, end)), safe=False
        )


urlpatterns = [
    # Need to have a / for grafana-json-plugin
    path("", Help.as_view(), name="help"),
    path("query", Query.as_view(), name="query"),
    path("search", Search.as_view(), name="search"),
]
