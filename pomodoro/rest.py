import collections
import datetime
import json
import logging
import time

import pytz
from rest_framework import viewsets
from rest_framework.authentication import (BasicAuthentication, SessionAuthentication,
                                           TokenAuthentication)
from rest_framework.decorators import list_route, detail_route
from pomodoro.models import Favorite, Pomodoro
from pomodoro.permissions import IsOwner
from pomodoro.renderers import CalendarRenderer
from pomodoro.serializers import FavoriteSerializer, PomodoroSerializer
from django.http import JsonResponse
from django.utils import timezone
from django.utils.timezone import make_aware

try:
    from timezone.models import Timezone
except ImportError:
    Timezone = None

DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'
NOCATEGORY = '{Uncategorized}'

logger = logging.getLogger(__name__)


def floorts(ts):
    return ts.replace(minute=0, hour=0, second=0, microsecond=0)


class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = (IsOwner,)
    authentication_classes = (BasicAuthentication, SessionAuthentication, TokenAuthentication)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        """
        Return Favorites owned by current user only
        """
        return Favorite.objects.filter(owner=self.request.user)

    @detail_route(methods=['post'])
    def start(self, request, pk):
        '''Quickstart a Pomodoro'''
        favorite = self.get_object()
        now = timezone.now().replace(microsecond=0)
        try:
            pomodoro = Pomodoro.objects\
                .filter(owner=request.user).latest('start')
        except Pomodoro.DoesNotExist:
            # Handle the case for a new user that does not have any
            # pomodoros at all
            pass
        else:
            if pomodoro.end > now:
                return JsonResponse({
                    'message': 'Cannot replace active pomodoro',
                    'data': PomodoroSerializer(pomodoro).data
                }, status=409)

        pomodoro = Pomodoro()
        pomodoro.title = favorite.title
        pomodoro.category = favorite.category
        pomodoro.owner = request.user
        pomodoro.start = now
        pomodoro.end = pomodoro.start + datetime.timedelta(minutes=favorite.duration)
        pomodoro.save()

        return JsonResponse(PomodoroSerializer(pomodoro).data, status=201)


class PomodoroViewSet(viewsets.ModelViewSet):
    """
    Basic Pomodoro API without any extra
    """
    queryset = Pomodoro.objects.all()
    serializer_class = PomodoroSerializer
    permission_classes = (IsOwner,)
    authentication_classes = (BasicAuthentication, SessionAuthentication, TokenAuthentication)
    renderer_classes = viewsets.ModelViewSet.renderer_classes + [CalendarRenderer]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_today(self):
        return floorts(timezone.localtime(timezone.now()))

    @list_route(methods=['post'], authentication_classes=[BasicAuthentication])
    def query(self, request):
        '''Grafana Query'''
        body = json.loads(request.body.decode("utf-8"))
        start = make_aware(
            datetime.datetime.strptime(body['range']['from'], DATETIME_FORMAT),
            pytz.utc)
        end = make_aware(
            datetime.datetime.strptime(body['range']['to'], DATETIME_FORMAT),
            pytz.utc)

        results = []
        durations = collections.defaultdict(lambda: collections.defaultdict(int))

        if Timezone:
            tzname = Timezone.objects.filter(owner=request.user)
            timezone.activate(pytz.timezone(tzname[0].timezone))
            tzinfo = pytz.timezone(tzname[0].timezone)

            start = start.astimezone(tzinfo)
            end = end.astimezone(tzinfo)

        _ts = floorts(start)
        dates = []
        for offset in range(0, (end - start).days + 1):
            dates.append(_ts + datetime.timedelta(days=offset))

        for target in body['targets']:
            _search = '' if target['target'] == NOCATEGORY else target['target']
            for pomodoro in Pomodoro.objects\
                    .filter(owner=self.request.user)\
                    .filter(category=_search)\
                    .filter(start__gte=start)\
                    .filter(end__lte=end):
                # Bucket by midnight. If we have a timezone object, ensure we're in the right timezone
                if Timezone:
                    started = pomodoro.start.astimezone(tzinfo)
                    completed = pomodoro.end.astimezone(tzinfo)
                else:
                    started = pomodoro.start
                    completed = pomodoro.end

                if started.date() == completed.date():
                    durations[floorts(started)][target['target']] += pomodoro.duration.total_seconds()
                else:
                    midnight = floorts(completed)
                    durations[floorts(started)][target['target']] += (midnight - started).total_seconds()
                    durations[floorts(completed)][target['target']] += (completed - midnight).total_seconds()

        for target in body['targets']:
            response = {
                'target': target['target'],
                'datapoints': []
            }

            for ts in dates:
                unixtimestamp = time.mktime(ts.timetuple()) * 1000
                response['datapoints'].append([durations[ts][target['target']], unixtimestamp])
            results.append(response)
        return JsonResponse(results, safe=False)

    @list_route(methods=['post'], authentication_classes=[BasicAuthentication])
    def search(self, request):
        '''Grafana Search'''
        categories = list(Pomodoro.objects
            .filter(owner=self.request.user)
            .exclude(category='')
            .order_by('category')
            .values_list('category', flat=True)
            .distinct('category')
        )
        return JsonResponse([NOCATEGORY] + categories, safe=False)

    def get_queryset(self):
        return Pomodoro.objects.filter(owner=self.request.user)
