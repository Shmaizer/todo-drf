from rest_framework import serializers

from ..tasks.models import Task
from ..users.models import User
from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    task_id = serializers.PrimaryKeyRelatedField(
        queryset=Task.objects.all(),
        source="task",
    )

    author_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="author",
    )

    class Meta:
        model = Comment
        fields = ["task_id", "author_id", "text", "created_at", "updated_at"]

    def create(self, validated_data):
        return Comment.objects.create(
            task=self.context["task"],
            author=self.context["author"],
            text=validated_data["text"],
            created_at=validated_data["created_at"],
            updated_at=validated_data["updated_at"],
        )
