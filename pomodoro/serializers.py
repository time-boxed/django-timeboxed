from rest_framework import serializers

from . import models

from django.contrib.sites.shortcuts import get_current_site
from django.utils import timezone


class LinkField(serializers.Field):
    def __init__(self, **kwargs):
        kwargs["source"] = "get_absolute_url"
        kwargs["read_only"] = True
        super().__init__(**kwargs)

    def to_representation(self, value):
        return "https://" + get_current_site(None).domain + value


class FavoriteSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")
    html_link = LinkField()

    class Meta:
        model = models.Favorite
        fields = "__all__"
        read_only = ("id", "icon", "count", "owner")


class PomodoroSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")
    html_link = LinkField()

    def create(self, validated_data):
        if "start" not in validated_data:
            validated_data["start"] = timezone.now()
        return models.Pomodoro.objects.create(**validated_data)

    class Meta:
        model = models.Pomodoro
        fields = "__all__"
        read_only_fields = ("id", "owner")
