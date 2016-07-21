import collections
import datetime
import json
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

from django.http import JsonResponse
from django.utils import timezone
from django.utils.timezone import make_aware

try:
    from timezone.models import Timezone
except ImportError:
    Timezone = None

DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'


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
            for pomodoro in Pomodoro.objects\
                    .filter(owner=self.request.user)\
                    .filter(category=target['target'])\
                    .filter(created__gte=start)\
                    .filter(created__lte=end):
                # Bucket by midnight. If we have a timezone object, ensure we're in the right timezone
                if Timezone:
                    started = pomodoro.created.astimezone(tzinfo)
                    completed = pomodoro.completed.astimezone(tzinfo)
                else:
                    started = pomodoro.created
                    completed = pomodoro.completed

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
        return JsonResponse(list(Pomodoro.objects
            .filter(owner=self.request.user)
            .exclude(category='')
            .order_by('category')
            .values_list('category', flat=True)
            .distinct('category')
            ), safe=False)

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
                return qs.filter(created__gte=today)
            if date == 'yesterday':
                today = self.get_today()
                yesterday = today - datetime.timedelta(days=1)
                return qs.filter(created__gte=yesterday, created__lt=today)
        else:
            days = int(self.request.query_params.get('days', 7))
            created_after = self.get_today() - datetime.timedelta(days=days)
            return qs.filter(created__gte=created_after)
        return qs

    @list_route(methods=['post'])
    def append(self, request, *args, **kwargs):
        '''
        Log time spent on a pomodoro

        This route is intended as a quick time logger. If there is an existing match for the pomodoro,
        time will be appended, otherwise a new pomodoro object will be created
        '''
        self.object = None
        self.created = False

        # Check to see if we have an active pomodoro already
        for pomodoro in Pomodoro.objects.filter(owner=self.request.user, title=request.data['title']):
            if pomodoro.completed + datetime.timedelta(minutes=2 * int(request.data['duration'])) > timezone.now():
                self.object = pomodoro
                self.created = True

        serializer = self.get_serializer(self.object, data=request.data, partial=True)

        if serializer.is_valid():
            # Make sure we don't lose our existing time
            if self.object:
                serializer.validated_data['duration'] += self.object.duration

            self.object = serializer.save(owner=self.request.user)
            status_code = self.created and status.HTTP_201_CREATED or status.HTTP_200_OK
            return Response(serializer.validated_data, status=status_code)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
