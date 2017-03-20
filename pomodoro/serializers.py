from rest_framework import serializers
from pomodoro.models import Favorite, Pomodoro
from django.utils import timezone


class FavoriteSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Favorite
        fields = ('id', 'title', 'duration', 'category', 'owner', 'icon', 'count',)
        read_only = ('id', 'icon', 'count',)


class PomodoroSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    def create(self, validated_data):
        if 'start' not in validated_data:
            validated_data['start'] = timezone.now()
        return Pomodoro.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.start = validated_data.get('start', instance.start)
        instance.end = validated_data.get('end', instance.end)
        instance.category = validated_data.get('category', instance.category)
        instance.save()
        return instance

    class Meta:
        model = Pomodoro
        fields = ('id', 'title', 'start', 'end', 'category', 'owner',)
        read_only_fields = ('id',)
