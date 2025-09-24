from rest_framework import viewsets

from apps.tags.models import Tag
from apps.tags.serializers import TagsSerializer


class TagsViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagsSerializer
