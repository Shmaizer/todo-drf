from django.db import models

from ..tags.models import Tag
from ..tasks.models import Task


class TaskTag(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    tags = models.ForeignKey(Tag, on_delete=models.CASCADE)
