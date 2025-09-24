from rest_framework import serializers

from ..users.models import User
from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    owner_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="owner",
        allow_null=True,
    )
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
        return Task.objects.create(
            title=validated_data["title"],
            description=validated_data["description"],
            due_date=validated_data["due_date"],
            status=validated_data["status"],
            priority=validated_data["priority"],
            owner=validated_data["owner"],
            assigned=validated_data["assigned"],
        )
