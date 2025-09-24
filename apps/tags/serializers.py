from rest_framework import serializers

from .models import Tag


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name")
        read_only_fields = ("id",)

    def create(self, validated_data):
        return Tag.objects.create(**validated_data)
