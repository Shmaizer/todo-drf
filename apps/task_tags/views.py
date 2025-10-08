from django.db import IntegrityError, transaction
from django.http import Http404
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..tags.models import Tag
from ..tags.serializers import TagSerializer
from ..tasks.models import Task
from ..tasks.permissions import IsTaskOwnerOrAssignee
from .models import TaskTag
from .serializers import TaskTagSerializer


class TaskTagsDetailAPIView(APIView):
    permission_classes = [IsAuthenticated, IsTaskOwnerOrAssignee]

    def get_task(self, pk, request):
        try:
            task = Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            raise Http404("Task not found")
        self.check_object_permissions(request, task)
        return task

    def get(self, request, pk):
        task = self.get_task(pk, request)
        task_tags_queryset = (
            TaskTag.objects.filter(task=task)
            .select_related("tag")
            .order_by("tag__name")
        )
        tags = [tt.tag for tt in task_tags_queryset]
        serializer = TagSerializer(tags, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, pk):
        """
        {
            "tags": [1, 2, 3]
        }
        """
        task = self.get_task(pk, request)
        tag_list = request.data.get("tags")
        if not tag_list:
            return Response(
                {"detail": "Field 'tags' is requred"}, status=status.HTTP_403_FORBIDDEN
            )
        if not isinstance(tag_list, (list, tuple)):
            return Response(
                {"detail": "Field 'tags' should be a list or tuple"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        normalized_list = []
        for tag in tag_list:
            try:
                normalized_list.append(int(tag))
            except (ValueError, TypeError):
                return Response(
                    {"detail": "Uncorrect ID tag"}, status=status.HTTP_400_BAD_REQUEST
                )
        normalized_list = list(dict.fromkeys(normalized_list))
        if not normalized_list:
            return Response(
                {"detail": "List 'tags' empty"}, status=status.HTTP_400_BAD_REQUEST
            )

        tags = list(Tag.objects.filter(id__in=normalized_list))
        found_list = {t.id for t in tags}
        missing_list = [tagId for tagId in normalized_list if tagId not in found_list]
        if missing_list:
            return Response(
                {"detail": "Non-existent tags found"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        existing_tag_list = set(
            TaskTag.objects.filter(task=task, tag__in=normalized_list).values_list(
                "tag_id", flat=True
            )
        )
        to_create = []
        for tag in tags:
            if tag.id not in existing_tag_list:
                to_create.append(TaskTag(task=task, tag=tag))

        to_create = [
            TaskTag(task=task, tag=tag)
            for tag in tags
            if tag.id not in existing_tag_list
        ]

        if to_create:
            try:
                with transaction.atomic():
                    TaskTag.objects.bulk_create(to_create)
            except IntegrityError:
                pass

        serializer = TagSerializer([tt.tag for tt in task.task_tags.all()], many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TaskTagsDeleteAPIView(APIView):
    def get_task(self, pk, request):
        try:
            task = Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            raise Http404("Task not found")
        self.check_object_permissions(request, task)
        return task

    def delete(self, request, pk, tag_id):
        task = self.get_task(pk, request)
        try:
            task_tag = TaskTag.objects.get(task=task, tag_id=tag_id)
        except TaskTag.DoesNotExist:
            return Response(
                {"detail": "Task not found"}, status=status.HTTP_404_NOT_FOUND
            )
        task_tag.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
