from rest_framework import serializers

from pomodoro.models import Favorite, Pomodoro, Tag


class TagSeralizer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("title",)

    def to_representation(self, instance):
        return instance.title

    def to_internal_value(self, data):
        return {"title": data}


class FavoriteSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")
    tags = TagSeralizer(many=True, required=False)

    class Meta:
        model = Favorite
        fields = ("id", "title", "duration", "owner", "icon", "count", "tags")
        read_only = ("id", "icon", "count")


class PomodoroSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")
    tags = TagSeralizer(many=True, required=False)

    class Meta:
        model = Pomodoro
        fields = ("id", "title", "start", "end", "owner", "tags")
        read_only_fields = ("id",)

    def create(self, validated_data):
        # Pop our tags off so we can process them later
        tags = validated_data.pop("tags", [])

        # Create our pomodoro object
        pomodoro = Pomodoro.objects.create(**validated_data)

        # Process our tags using the same owner as our pomodoro
        newtags = [
            Tag.objects.get_or_create(owner=pomodoro.owner, **tag) for tag in tags
        ]

        # Set the new tag list while dropping the 'created' field
        pomodoro.tags.set([x[0] for x in newtags])

        return pomodoro
