from django.db import models

from ..users.models import User

# Create your models here.


class Task(models.Model):
    class TaskStatus(models.TextChoices):
        NEW = "NEW", "New"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        COMPLETED = "COMPLETED", "Completed"

    class TaskPriority(models.TextChoices):
        LOW = "LOW", "Low"
        MEDIUM = "MEDIUM", "Medium"
        HIGH = "HIGH", "High"

    title = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=11, choices=TaskStatus.choices, default=TaskStatus.NEW
    )
    priority = models.CharField(
        max_length=10, choices=TaskPriority.choices, default=TaskPriority.MEDIUM
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="owner_tasks",
    )
    assigned = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="assigned_tasks",
        blank=True,
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    class Meta:
        indexes = [models.Index(fields=["status", "priority", "due_date"])]
