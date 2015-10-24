import datetime
from rest_framework import serializers
from pomodoro.models import Pomodoro, Favorite


class FavoriteSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Favorite
        fields = ('title', 'duration', 'category', 'owner')



class PomodoroSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    def create(self, validated_data):
        if 'created' not in validated_data:
            validated_data['created'] = datetime.datetime.utcnow()
        return Pomodoro.objects.create(**validated_data)

    class Meta:
        model = Pomodoro
        fields = ('title', 'duration', 'category', 'owner', 'created')
