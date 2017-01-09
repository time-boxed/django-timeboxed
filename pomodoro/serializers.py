from rest_framework import serializers
from pomodoro.models import Favorite, Pomodoro
from django.utils import timezone


class FavoriteSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Favorite
        fields = ('id', 'title', 'duration', 'category', 'owner', 'icon')
        read_only = ('id', 'icon',)


class PomodoroSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    def create(self, validated_data):
        if 'created' not in validated_data:
            validated_data['created'] = timezone.now()
        return Pomodoro.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.duration = validated_data.get('duration', instance.duration)
        instance.category = validated_data.get('category', instance.category)
        instance.save()
        return instance

    class Meta:
        model = Pomodoro
        fields = ('id', 'title', 'duration', 'category', 'owner', 'created')
        read_only_fields = ('id',)
