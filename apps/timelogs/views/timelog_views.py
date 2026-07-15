from rest_framework import generics
from rest_framework.exceptions import ValidationError
from common.permissions import HasWorkspaceProjectAccess
from timelogs.models import TimeLog
from timelogs.serializers import TimeLogSerializer
from tasks.models import Task


class TimeLogListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = TimeLogSerializer
    permission_classes = [HasWorkspaceProjectAccess]
    read_roles = ["Admin", "Manager", "Member"]
    write_roles = ["Admin", "Manager", "Member"]

    def get_queryset(self):
        return TimeLog.objects.filter(task_id=self.kwargs["task_id"])

    def perform_create(self, serializer):
        task = generics.get_object_or_404(Task, id=self.kwargs["task_id"])
        # Ensure workspace match
        if task.project.workspace_id != self.kwargs["workspace_id"]:
            raise ValidationError("Task does not belong to the active workspace.")
        serializer.save(user=self.request.user, task=task)


class TimeLogDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TimeLog.objects.all()
    serializer_class = TimeLogSerializer
    permission_classes = [HasWorkspaceProjectAccess]
    read_roles = ["Admin", "Manager", "Member"]
    write_roles = ["Admin", "Manager", "Member"]
    delete_roles = ["Admin", "Manager", "Member"]

    def perform_update(self, serializer):
        log = self.get_object()
        if log.is_locked:
            raise ValidationError("This time log is locked and cannot be modified.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.is_locked:
            raise ValidationError("This time log is locked and cannot be deleted.")
        instance.delete()
