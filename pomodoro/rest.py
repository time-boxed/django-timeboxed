from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.settings import api_settings

from . import filters, models, permissions, renderers, serializers

from django.http import JsonResponse
from django.utils import timezone


class BaseViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsOwner,)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user)


class FavoriteViewSet(BaseViewSet):
    queryset = models.Favorite.objects
    serializer_class = serializers.FavoriteSerializer

    @action(detail=True, methods=["post"])
    def start(self, request, pk):
        """Quickstart a Pomodoro"""
        now = timezone.now().replace(microsecond=0)
        try:
            pomodoro = models.Pomodoro.objects.filter(owner=request.user).latest(
                "start"
            )
        except models.Pomodoro.DoesNotExist:
            # Handle the case for a new user that does not have any
            # pomodoros at all
            pass
        else:
            if pomodoro.end > now:
                return JsonResponse(
                    {
                        "message": "Cannot replace active pomodoro",
                        "data": serializers.PomodoroSerializer(pomodoro).data,
                    },
                    status=status.HTTP_409_CONFLICT,
                )

        pomodoro = self.get_object().start(now)
        return JsonResponse(
            serializers.PomodoroSerializer(pomodoro).data,
            status=status.HTTP_201_CREATED,
        )


class PomodoroViewSet(BaseViewSet):
    queryset = models.Pomodoro.objects.prefetch_related("project")
    serializer_class = serializers.PomodoroSerializer
    filter_backends = [filters.DateFilter]
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES + [
        renderers.CalendarRenderer
    ]


class ProjectViewSet(BaseViewSet):
    queryset = models.Project.objects
    serializer_class = serializers.ProjectSeralizer
