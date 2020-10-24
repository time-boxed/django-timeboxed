from logging import raiseExceptions
from rest_framework import serializers

from . import models

from django.contrib.sites.shortcuts import get_current_site


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
    url = URLField(required=False)

    class Meta:
        model = models.Project
        exclude = ("owner",)
        read_only_fields = ("id",)


class NestedProject(ProjectSeralizer):
    def to_internal_value(self, data):
        # if we have just a string, then we assume that we have just the
        # project pk, otherwise we assume it's the full data block.
        if isinstance(data, str):
            return {"id": data}
        return data


class FavoriteSerializer(serializers.ModelSerializer):
    html_link = LinkField()
    url = URLField(required=False)
    project = NestedProject()

    class Meta:
        model = models.Favorite
        exclude = ("owner",)
        read_only_fields = ("id", "icon", "count")


class PomodoroSerializer(serializers.ModelSerializer):
    html_link = LinkField()
    url = URLField(required=False)
    project = NestedProject()

    def create(self, validated_data):
        validated_data["project_id"] = validated_data.pop("project")["id"]
        return models.Pomodoro.objects.create(**validated_data)

    class Meta:
        model = models.Pomodoro
        exclude = ("owner",)
        read_only_fields = ("id",)
