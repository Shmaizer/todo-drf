from django.db import models
from django.db.models.functions import Lower


class Tag(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = 'tag'
        constraints = [models.UniqueConstraint(Lower('name'), name='unique_tag_name')]

    def __str__(self):
        return self.name
