from rest_framework import serializers

from ..users.models import User
from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    assigned_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source="assigned", allow_null=True, required=False
    )

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "created_at",
            "updated_at",
            "due_date",
            "status",
            "priority",
            "owner_id",
            "assigned_id",
            "is_active",
        ]

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data["owner"] = request.user
        return Task.objects.create(**validated_data)
