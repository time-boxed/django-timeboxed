from rest_framework import serializers
from pomodoro.models import Pomodoro


class PomodoroSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Pomodoro
        fields = ('title', 'duration', 'category', 'owner', 'created')
