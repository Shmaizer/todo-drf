from django.contrib.auth import get_user_model
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..users.authentication import JWTAuthentication
from .models import Task
from .permissions import IsTaskOwnerOrAssignee
from .serializers import TaskSerializer

# class TaskViewSet(viewsets.ModelViewSet):
#     queryset = Task.objects.all()
#     serializer_class = TaskSerializer
#     def get_queryset(self):
#         return Task.objects.filter(
#             Q(owner=self.request.user) | Q(assigned=self.request.user.id)
#         ).distinct()


class TaskListCreateAPIView(APIView):
    def get(self, request, *args):
        task_query = Task.objects.filter(
            Q(owner=self.request.user) | Q(assigned=self.request.user.id)
        ).distinct()
        serializer = TaskSerializer(task_query, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args):
        serializer = TaskSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskDetailAPIView(APIView):
    permission_classes = [IsAuthenticated, IsTaskOwnerOrAssignee]

    def get_object(self, pk, request):
        try:
            task = Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            # raise PermissionDenied("Not have permission to access this task")
            raise Http404("Page not found")
        self.check_object_permissions(request, task)
        return task

    def get(self, request, pk):
        task = self.get_object(pk, request)
        serializer = TaskSerializer(task)
        return Response(serializer.data)

    def put(self, request, pk):
        task = self.get_object(pk, request)
        serializer = TaskSerializer(task, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        task = self.get_object(pk, request)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


User = get_user_model()


class TaskAssignAPIView(APIView):
    permission_classes = [IsAuthenticated, IsTaskOwnerOrAssignee]

    def get_object(self, pk, request):
        task = Task.objects.get(pk=pk)
        self.check_object_permissions(request, task)
        return task

    def patch(self, request, pk):
        """
        Waiting for payload:
        {
            "assigned_id": <user_id> or null
        }
        """
        task = self.get_object(pk, request)
        if task.owner != request.user:
            return Response(
                {"detail": "You do not have permission to perform this action"},
                status=status.HTTP_403_FORBIDDEN,
            )
        assigned_id = request.data.get('assigned_id', None)
        if assigned_id is None:
            task.assigned = assigned_id
        else:
            try:
                assigned_user = User.objects.get(id=assigned_id)
            except User.DoesNotExist:
                raise Http404("User does not found")
            task.assigned = assigned_user
        task.save(update_fields=['assigned'])
        serializer = TaskSerializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TaskStatusAPIView(APIView):
    permission_classes = [IsAuthenticated, IsTaskOwnerOrAssignee]

    def get_object(self, pk, request):
        task = Task.objects.get(pk=pk)
        self.check_object_permissions(request, task)
        return task

    def patch(self, request, pk):
        """
        Waiting for payload:
        {
            "status": "NEW" | "IN_PROGRESS" | "COMPLETED"
        }
        """
        task = self.get_object(pk, request)
        new_status = request.data.get("status", "NEW")
        if task.owner != request.user:
            return Response(
                {"detail": "You do not have permission to perform this action"},
                status=status.HTTP_403_FORBIDDEN,
            )
        if new_status not in Task.TaskStatus.values:
            return Response(
                {"detail": f"Invalid status: {new_status}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        task.status = new_status
        task.save(update_fields=['status'])
        serializer = TaskSerializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TaskPriorityAPIView(APIView):
    permission_classes = [IsAuthenticated, IsTaskOwnerOrAssignee]

    def get_object(self, pk, request):
        task = Task.objects.get(pk=pk)
        self.check_object_permissions(request, task)
        return task

    def patch(self, request, pk):
        """
        Waiting for payload:
        {
            "priority": "LOW" | "MEDIUM" | "HIGH"
        }
        """
        task = self.get_object(pk, request)
        priority = request.data.get("priority", "LOW")
        if task.owner != request.user:
            return Response(
                {"detail": "You do not have permission to perform this action"},
                status=status.HTTP_403_FORBIDDEN,
            )
        if priority not in Task.TaskPriority.values:
            return Response(
                {"detail": f"Invalid priority: {priority}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        task.priority = priority
        task.save(update_fields=['priority'])
        serializer = TaskSerializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)
