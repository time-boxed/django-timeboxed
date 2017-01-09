import collections
import datetime
import json
import logging
import time

import pytz
from rest_framework import status, viewsets
from rest_framework.authentication import (BasicAuthentication,
                                           SessionAuthentication,
                                           TokenAuthentication)
from rest_framework.decorators import list_route
from rest_framework.response import Response

from pomodoro.models import Favorite, Pomodoro
from pomodoro.permissions import IsOwner
from pomodoro.renderers import CalendarRenderer
from pomodoro.serializers import FavoriteSerializer, PomodoroSerializer

from django.core.exceptions import ObjectDoesNotExist
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
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        """
        Return Favorites owned by current user only
        """
        return Favorite.objects.filter(owner=self.request.user)

class PomodoroViewSet(viewsets.ModelViewSet):
    """
    Basic Pomodoro API without any extra
    """
    queryset = Pomodoro.objects.all()
    serializer_class = PomodoroSerializer
    permission_classes = (IsOwner,)
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)
    renderer_classes = viewsets.ModelViewSet.renderer_classes + [CalendarRenderer]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_today(self):
        return floorts(timezone.localtime(timezone.now()))

    @list_route(methods=['post'])
    def query(self, request):
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
                    durations[floorts(started)][target['target']] += pomodoro.duration
                else:
                    midnight = floorts(completed)
                    durations[floorts(started)][target['target']] += (midnight - started).total_seconds() / 60
                    durations[floorts(completed)][target['target']] += (completed - midnight).total_seconds() / 60

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

    @list_route(methods=['post'])
    def search(self, request):
        categories = list(Pomodoro.objects
            .filter(owner=self.request.user)
            .exclude(category='')
            .order_by('category')
            .values_list('category', flat=True)
            .distinct('category')
        )
        return JsonResponse([NOCATEGORY] + categories, safe=False)

    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        qs = Pomodoro.objects.filter(owner=self.request.user)
        date = self.request.query_params.get('date')
        if date:
            if date == 'today':
                today = self.get_today()
                return qs.filter(start__gte=today)
            if date == 'yesterday':
                today = self.get_today()
                yesterday = today - datetime.timedelta(days=1)
                return qs.filter(start__gte=yesterday, end__lt=today)
        else:
            days = int(self.request.query_params.get('days', 7))
            created_after = self.get_today() - datetime.timedelta(days=days)
            return qs.filter(start__gte=created_after)
        return qs

    @list_route(methods=['post'])
    def append(self, request, *args, **kwargs):
        '''
        Log time spent on a pomodoro

        This route is intended as a quick time logger. If there is an existing match for the pomodoro,
        time will be appended, otherwise a new pomodoro object will be created
        '''
        serializer = self.get_serializer(data=request.data, partial=True)
        if serializer.is_valid():
            logger.debug('Valid serializer %s', serializer.validated_data)
            try:
                # We fuzz our search by about 15 seconds to account for clock
                # drift between computers
                search_start = serializer.validated_data['start'] - datetime.timedelta(seconds=15)
                logger.debug('Searching from %s', search_start)
                pomodoro = Pomodoro.objects.filter(owner=self.request.user)\
                    .filter(title=serializer.validated_data['title'])\
                    .filter(end__gte=search_start)\
                    .get()
            except ObjectDoesNotExist:
                logger.debug('Creating new object')
                obj = serializer.save(owner=self.request.user)
                return Response(serializer.validated_data, status=status.HTTP_201_CREATED)
            else:
                logger.debug('Updating old object')
                serializer = self.get_serializer(pomodoro, data=request.data, partial=True)
                if serializer.is_valid():
                    # Make sure we keep the original start time
                    serializer.validated_data['start'] = pomodoro.start
                    obj = serializer.save(owner=self.request.user)
                    return Response(serializer.validated_data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
