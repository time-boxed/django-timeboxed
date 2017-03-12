from pomodoro import models
from django.forms import ModelForm


class PomodoroForm(ModelForm):
    class Meta:
        model = models.Pomodoro
        fields = ['title', 'category']
