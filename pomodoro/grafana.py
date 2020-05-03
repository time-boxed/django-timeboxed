import collections
import datetime
import json
import logging

from dateutil.parser import parse
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from . import models, util

from django.http import JsonResponse
from django.urls import path
from django.utils import timezone
from django.views.generic.base import TemplateView

logger = logging.getLogger(__name__)


class Help(TemplateView):

    template_name = "pomodoro/grafana/help.html"


class Search(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    def post(self, request, **kwargs):
        query = json.loads(request.body.decode("utf8"))
        logger.debug("search %s", query)
        return JsonResponse(
            [
                project.name
                for project in models.Project.objects.filter(
                    owner=self.request.user, active=True
                )
            ],
            safe=False,
        )



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
                util.floor(start + datetime.timedelta(days=x))
                for x in range(0, (end - start).days + 1)
            ]
        )

        # Loop through our targets, getting a date,timedelta pair that we
        # can bucket
        for t in targets:
            target = t["target"]
            for date, duration in self.filter(
                project__name=target,
                start__gte=start,
                end__lte=end,
                owner=self.request.user,
            ):
                bucket = util.floor(date)
                durations[target][bucket] += duration

        # Loop through our targets and buckets to build format that Grafana expects
        for target in durations:
            yield {
                "target": target,
                "datapoints": [
                    [durations[target][bucket].total_seconds(), util.to_ts(bucket)]
                    for bucket in buckets
                ],
            }

    def filter(self, **kwargs):
        """
        Taking kwargs as our django filter, loop through our pomodoro
        queryset, and return timedelta objects bucketed by date
        """
        for pomodoro in models.Pomodoro.objects.filter(**kwargs):
            start = timezone.localtime(pomodoro.start)
            end = timezone.localtime(pomodoro.end)
            # if there is no overlap, then we can return just the
            # difference of our start and end times
            if start.date() == end.date():
                yield start, end - start
            # otherwise, we need to return the part before midnight
            # and the part after midnight as two objects
            else:
                # TODO: Fix for multiple day events
                midnight = util.floor(end)
                yield start, midnight - start
                yield end, end - midnight

    def post(self, request, **kwargs):
        # https://github.com/grafana/simple-json-datasource#query-api
        query = json.loads(request.body.decode("utf8"))
        start = timezone.localtime(parse(query["range"]["from"]))
        end = timezone.localtime(parse(query["range"]["to"]))

        try:
            timezone.activate(request.timezone.timezone)
        except AttributeError:
            timezone.deactivate()
        else:
            start = timezone.localtime(start)
            end = timezone.localtime(end)

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
