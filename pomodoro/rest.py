from rest_framework import permissions, viewsets
from rest_framework.authentication import (BasicAuthentication,
                                           SessionAuthentication,
                                           TokenAuthentication)

from pomodoro.models import Pomodoro
from pomodoro.serializers import PomodoroSerializer
from pomodoro.permissions import IsOwner


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
