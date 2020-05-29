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


class URLField(serializers.URLField):
    def to_representation(self, value):
        if not value:
            return None
        return value


class ProjectSeralizer(serializers.ModelSerializer):
    html_link = LinkField()
    url = URLField()

    class Meta:
        model = models.Project
        exclude = ("owner",)
        read_only = "id"


class ShortProjectSeralizer(serializers.ModelSerializer):
    class Meta:
        model = models.Project
        exclude = ("owner", "memo", "url")
        read_only = "id"


class FavoriteSerializer(serializers.ModelSerializer):
    # project = ShortProjectSeralizer()
    html_link = LinkField()
    url = URLField()

    class Meta:
        model = models.Favorite
        exclude = ("owner",)
        read_only = ("id", "icon", "count")


class PomodoroSerializer(serializers.ModelSerializer):
    # project = ShortProjectSeralizer()
    html_link = LinkField()
    url = URLField()

    def create(self, validated_data):
        if "start" not in validated_data:
            validated_data["start"] = timezone.now()
        return models.Pomodoro.objects.create(**validated_data)

    class Meta:
        model = models.Pomodoro
        exclude = ("owner",)
        read_only_fields = ("id",)
