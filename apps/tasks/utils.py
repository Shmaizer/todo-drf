from django.http import Http404

from ..tasks.models import Task


def get_task_or_404(pk, request=None, self_instance=None):
    try:
        task = Task.objects.get(pk=pk)
    except Task.DoesNotExist:
        raise Http404("Task not found")
    self_instance.check_object_permissions(request, task)
    return task
