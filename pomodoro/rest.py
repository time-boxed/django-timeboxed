import collections
import datetime
import json

import pytz
from django.http import Http404, HttpResponse
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.authentication import (BasicAuthentication,
                                           SessionAuthentication,
                                           TokenAuthentication)
from rest_framework.decorators import list_route
from rest_framework.response import Response

from pomodoro.models import Favorite, Pomodoro
from pomodoro.permissions import IsOwner
from pomodoro.serializers import FavoriteSerializer, PomodoroSerializer


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

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        return Pomodoro.objects.filter(owner=self.request.user)

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
                    row.append({'v': durations[date][key] / 60})
            dataset['rows'].append({'c': row})

        response = HttpResponse(content_type='application/json')
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
