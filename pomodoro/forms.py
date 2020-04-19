from django.forms import ModelForm

from . import models


class PomodoroForm(ModelForm):
    class Meta:
        model = models.Pomodoro
        fields = ["title", "project"]

    def __init__(self, owner, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["project"].queryset = models.Project.objects.filter(owner=owner)
