from . import models

from django import forms


class PomodoroForm(forms.ModelForm):
    duration = forms.IntegerField()

    class Meta:
        model = models.Pomodoro
        fields = ["title", "project", "duration"]

    def __init__(self, owner, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["project"].queryset = models.Project.objects.filter(owner=owner)


class PomodoroEdit(forms.ModelForm):
    class Meta:
        model = models.Pomodoro
        fields = ["title", "project", "start", "end", "memo"]

    def __init__(self, owner, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["project"].queryset = models.Project.objects.filter(owner=owner)
