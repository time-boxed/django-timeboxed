import collections
import datetime
import json
import logging

from dateutil.parser import parse
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from . import models

from django.http import JsonResponse
from django.urls import path
from django.utils import timezone
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


def floor(dt):
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


class Query(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    def datapoints(self, targets, start, end):
        durations = collections.defaultdict(
            lambda: collections.defaultdict(datetime.timedelta)
        )
        # Define our buckets here, so that any days without metrics
        # are shown as 0
        buckets = sorted(
            [
                floor(start + datetime.timedelta(days=x))
                for x in range(0, (end - start).days + 1)
            ]
        )

        for t in targets:
            target = "" if t["target"] == NOCATEGORY else t["target"]
            for date, duration in self.fetch(target, start, end):
                bucket = floor(date)
                durations[bucket][target] += duration

        for t in targets:
            target = "" if t["target"] == NOCATEGORY else t["target"]
            yield {
                "target": target,
                "datapoints": [
                    [durations[bucket][target].total_seconds(), to_ts(bucket)]
                    for bucket in buckets
                ],
            }

    def fetch(self, target, start, end):
        for pomodoro in (
            models.Pomodoro.objects.filter(owner=self.request.user)
            .filter(category=target)
            .filter(start__gte=start)
            .filter(end__lte=end)
        ):
            if pomodoro.start.date() == pomodoro.end.date():
                yield pomodoro.start, pomodoro.end - pomodoro.start
            else:
                midnight = floor(pomodoro.end)
                yield pomodoro.start, midnight - pomodoro.start
                yield pomodoro.end, pomodoro.end - midnight

    def post(self, request, **kwargs):
        query = json.loads(request.body.decode("utf8"))
        start = timezone.localtime(parse(query["range"]["from"]))
        end = timezone.localtime(parse(query["range"]["to"]))

        logger.debug("%s %s %s", query, start, end)

        return JsonResponse(
            list(self.datapoints(query["targets"], start, end)), safe=False
        )


app_name = "grafana"
urlpatterns = [
    # Need to have a / for grafana-json-plugin
    path("", Help.as_view(), name="help"),
    path("query", Query.as_view(), name="query"),
    path("search", Search.as_view(), name="search"),
]
