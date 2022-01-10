from . import models


def pomodoro(request):
    context = {}
    if request.user.is_authenticated:
        context["latest_pomodoro"] = models.Pomodoro.objects.filter(owner=request.user).latest(
            "start"
        )
    return context
