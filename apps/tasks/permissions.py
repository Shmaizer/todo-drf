import logging

from rest_framework.permissions import BasePermission

from .models import Task

logger = logging.getLogger(__name__)


class IsTaskOwnerOrAssignee(BasePermission):
    def has_object_permission(self, request, view, obj):
        if not isinstance(obj, Task):
            return False

        logger.info(f"Request user: {request.user}")
        logger.info(f"Task owner: {obj.owner}")
        logger.info(f"Task assigned: {obj.assigned}")
        result = (obj.owner == request.user) or (obj.assigned == request.user)
        logger.info(f"Permission result: {result}")

        return result
