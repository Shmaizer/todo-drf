from django.db import models

from ..tags.models import Tag
from ..tasks.models import Task


class TaskTag(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='task_tags')
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name='tag_tasks')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('task', 'tag')
        db_table = 'task_tags'

    def __str__(self):
        return f'{self.task} - {self.tag}'
