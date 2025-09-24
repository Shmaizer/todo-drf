from rest_framework import serializers

from ..tags.models import Tag
from ..tasks.models import Task
from .models import TaskTag


class TaskTagSerializer(serializers.ModelSerializer):
    task_id = serializers.PrimaryKeyRelatedField(
        queryset=Task.objects.all(), source="task"
    )

    tags_id = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), source="tags"
    )

    class Meta:
        model = TaskTag
        fields = [
            "id",
            "task_id",
            "tags_id",
        ]

    def create(self, validated_data):
        return TaskTag.objects.create(
            task=validated_data["task"], tags=validated_data["tags"]
        )
