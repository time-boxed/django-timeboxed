import datetime
import json
import collections

from django.http import HttpResponse
from rest_framework import permissions, viewsets
from rest_framework.authentication import (BasicAuthentication,
                                           SessionAuthentication,
                                           TokenAuthentication)
from rest_framework.decorators import list_route

from pomodoro.models import Pomodoro
from pomodoro.permissions import IsOwner
from pomodoro.serializers import PomodoroSerializer


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
        def dateformat(date):
            return "Date(%d,%d,%d)" % (
                date.year, date.month - 1, date.day)
        dataset = {'cols': [
            {'id': 'Date', 'pattern': 'yyyy/MM/dd', 'type': 'date'},
        ], 'rows': []}

        lables = ['Untracked']
        durations = collections.defaultdict(lambda: collections.defaultdict(int))
        for pomodoro in Pomodoro.objects.filter(owner=self.request.user, created__gte=datetime.datetime.now() - datetime.timedelta(days=30)):
            if pomodoro.category not in lables:
                lables.append(pomodoro.category)

            durations[pomodoro.created.date()][pomodoro.category] += pomodoro.duration
            durations[pomodoro.created.date()]['Untracked'] -= pomodoro.duration
        # For now, ignore our untracked
        lables.remove('Untracked')
        for key in lables:
            dataset['cols'].append({'id': key, 'label': key, 'type': 'number'})

        for date in durations:
            row = []
            row.append({"v": dateformat(date)},)
            for key in lables:
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
