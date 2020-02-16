from rest_framework import serializers

from . import models

from django.utils import timezone


class FavoriteSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")

    class Meta:
        model = models.Favorite
        fields = "__all__"
        read_only = ("id", "icon", "count", "owner")


class PomodoroSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")

    def create(self, validated_data):
        if "start" not in validated_data:
            validated_data["start"] = timezone.now()
        return models.Pomodoro.objects.create(**validated_data)

    class Meta:
        model = models.Pomodoro
        fields = "__all__"
        read_only_fields = ("id", "owner")
