from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.tags.models import Tag
from apps.tags.serializers import TagSerializer


class TagsViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
