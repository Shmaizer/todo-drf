from django.db import models

from ..tasks.models import Task
from ..users.models import User


class Comment(models.Model):
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name='task_comment'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='author_comment'
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'comments'

    def __str__(self):
        return self.text
