from django.db.models import Q
from django.http import Http404
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..tasks.models import Task
from ..tasks.permissions import IsTaskOwnerOrAssignee
from .models import Comment
from .serializers import CommentSerializer


class CommentDetailAPIView(APIView):
    permission_classes = (IsAuthenticated, IsTaskOwnerOrAssignee)

    def get_task(self, pk, request):
        try:
            task = Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            raise Http404("Task not found")
        self.check_object_permissions(request, task)
        return task

    def get(self, request, pk):
        task = self.get_task(pk, request)
        comments = Comment.objects.filter(task=task)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, pk):
        task = self.get_task(pk, request)
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(task=task, author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
