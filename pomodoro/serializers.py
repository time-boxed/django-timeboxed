import datetime
from rest_framework import serializers
from pomodoro.models import Pomodoro


class PomodoroSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    def create(self, validated_data):
        if 'created' not in validated_data:
            validated_data['created'] = datetime.datetime.utcnow()
        return Pomodoro.objects.create(**validated_data)

    class Meta:
        model = Pomodoro
        fields = ('title', 'duration', 'category', 'owner', 'created')
