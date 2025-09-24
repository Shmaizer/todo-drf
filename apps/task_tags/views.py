from rest_framework import viewsets

from .models import TaskTag
from .serializers import TaskTagSerializer


class TaskTagsViewSet(viewsets.ModelViewSet):
    queryset = TaskTag.objects.all()
    serializer_class = TaskTagSerializer
