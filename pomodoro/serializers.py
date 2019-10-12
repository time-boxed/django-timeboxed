from rest_framework import serializers

from pomodoro.models import Favorite, Pomodoro

from django.utils import timezone


class FavoriteSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")

    class Meta:
        model = Favorite
        fields = "__all__"
        read_only = ("id", "icon", "count", "owner")


class PomodoroSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")

    def create(self, validated_data):
        if "start" not in validated_data:
            validated_data["start"] = timezone.now()
        return Pomodoro.objects.create(**validated_data)

    class Meta:
        model = Pomodoro
        fields = "__all__"
        read_only_fields = ("id", "owner")
