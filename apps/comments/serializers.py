from rest_framework import serializers

from ..tasks.models import Task
from ..users.models import User
from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "author_name", "text", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at", "author_name"]

    def create(self, validated_data):
        # request = self.context.get("request")
        # validated_data["author"] = request.user
        return Comment.objects.create(**validated_data)
