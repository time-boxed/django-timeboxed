import collections
import datetime
import json
import operator
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

from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.utils.timezone import make_aware

DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'


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

    def get_now(self):
        return timezone.localtime(timezone.now())

    def get_tomorrow(self):
        return self.get_today() + datetime.timedelta(days=1)

    def get_today(self):
        return timezone.localtime(timezone.now()).replace(hour=0, minute=0, second=0, microsecond=0)

    @list_route(methods=['post'])
    def query(self, request):
        body = json.loads(request.body.decode("utf-8"))
        start = make_aware(datetime.datetime.strptime(body['range']['from'], DATETIME_FORMAT))
        end = make_aware(datetime.datetime.strptime(body['range']['to'], DATETIME_FORMAT))

        results = []
        durations = collections.defaultdict(lambda: collections.defaultdict(int))

        for target in body['targets']:
            for pomodoro in Pomodoro.objects\
                    .filter(owner=self.request.user)\
                    .filter(category=target['target'])\
                    .filter(created__gte=start)\
                    .filter(created__lte=end)\
                    .order_by('created'):
                ts = time.mktime(pomodoro.created.replace(minute=0, hour=0, second=0).timetuple())
                durations[ts][target['target']] += pomodoro.duration

        for target in body['targets']:
            response = {
                'target': target['target'],
                'datapoints': []
            }
            for ts in sorted(durations.keys()):
                response['datapoints'].append([durations[ts][target['target']], ts  * 1000])
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

    @list_route()
    def pie(self, request):
        '''
        Create a Google DataView suitable for being rendered as a pie chart
        '''

        dataset = {'cols': [
            {'id': 'Category', 'type': 'string'},
            {'id': 'Duration', 'type': 'number'},
        ], 'rows': []}

        durations = collections.defaultdict(int)
        date = self.request.query_params.get('date')
        if date:
            durations['Unaccounted'] = 24 * 60
            if date == 'today':
                durations['Remainder'] = (self.get_tomorrow() - self.get_now()).seconds / 60
                durations['Unaccounted'] -= durations['Remainder']

        for pomodoro in self.get_queryset():
            durations[pomodoro.category] += pomodoro.duration
            if date:
                durations['Unaccounted'] -= pomodoro.duration

        for category, value in sorted(durations.items(), key=operator.itemgetter(1), reverse=True):
            dataset['rows'].append({'c': [{'v': category}, {'v': round(value / 60, 2)}]})

        response = HttpResponse(content_type='application/javascript')
        response.write('google.visualization.Query.setResponse(' + json.dumps({
            'version': '0.6',
            'table': dataset,
            'reqId': '0',
            'status': 'ok',
        }) + ');')
        return response

    @list_route()
    def datatable(self, request):
        tzname = request.session.get('django_timezone')

        def dateformat(date):
            return "Date(%d,%d,%d)" % (
                date.year, date.month - 1, date.day)
        dataset = {'cols': [
            {'id': 'Date', 'pattern': 'yyyy/MM/dd', 'type': 'date'},
        ], 'rows': []}

        lables = ['']
        days = int(request.query_params.get('days', 30))
        durations = collections.defaultdict(lambda: collections.defaultdict(int))
        for pomodoro in Pomodoro.objects.filter(owner=self.request.user, created__gte=timezone.now() - datetime.timedelta(days=days)):
            if pomodoro.category not in lables:
                lables.append(pomodoro.category)

            date = pomodoro.created.astimezone(pytz.timezone(tzname)).date() if tzname else pomodoro.created.date()

            durations[date][pomodoro.category] += pomodoro.duration
            durations[date]['Untracked'] -= pomodoro.duration
        # For now, ignore our untracked
        for key in sorted(lables):
            dataset['cols'].append({'id': key, 'label': key, 'type': 'number'})

        for date in durations:
            row = []
            row.append({"v": dateformat(date)},)
            for key in sorted(lables):
                if key == 'Untracked':
                    # Subtrack our 'Tracked' time from 24 hours with a 7 hour
                    # 'sleep' adjustment
                    row.append({'v': durations[date][key] / 60 + 24 - 7})
                else:
                    row.append({'v': round(durations[date][key] / 60, 2)})
            dataset['rows'].append({'c': row})

        response = HttpResponse(content_type='application/javascript')
        response.write('google.visualization.Query.setResponse(' + json.dumps({
            'version': '0.6',
            'table': dataset,
            'reqId': '0',
            'status': 'ok',
        }) + ');')
        return response

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
