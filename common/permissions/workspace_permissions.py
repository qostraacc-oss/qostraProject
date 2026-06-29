from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.http import Http404

class HasWorkspaceProjectAccess(BasePermission):
    """
    Standard DRF permission class for verifying workspace-to-project mappings.
    Checks:
    1. Workspace match (either creator's original workspace or member's mapped workspace).
    2. Role-based access control mapped to CRUD actions (read, write, delete).
    """

    # Secure fallback defaults
    default_read_roles = ["owner", "admin", "member", "viewer"]
    default_write_roles = ["owner", "admin"]
    default_delete_roles = ["owner", "admin"]

    def has_permission(self, request, view):
        workspace_id = view.kwargs.get("workspace_id")
        if not workspace_id:
            return False

        # If project_id is in the URL (typically for list/create views)
        project_id = view.kwargs.get("project_id")
        if project_id:
            from projects.models import Project
            project = get_object_or_404(Project, pk=project_id, archived_at__isnull=True)
            return self._verify_and_cache(request, workspace_id, project, view)

        return True

    def has_object_permission(self, request, view, obj):
        workspace_id = view.kwargs.get("workspace_id")
        if not workspace_id:
            return False

        # Get parent project using our common property interface
        project = getattr(obj, "project_context", None)
        if not project:
            raise Http404("Resource parent project not found.")

        return self._verify_and_cache(request, workspace_id, project, view)

    def _verify_and_cache(self, request, workspace_id, project, view):
        user = request.user
        
        # Check cache to prevent duplicate queries on the same request lifecycle
        if hasattr(request, "_workspace_project_member_cache"):
            cache = request._workspace_project_member_cache
            if cache.get("project") == project:
                return self._check_role(request, cache.get("member"), project, view)

        # 1. Creator Verification
        is_creator = project.created_by == user and str(project.workspace_id) == str(workspace_id)
        
        # 2. Member Verification
        from projects.models import ProjectMember
        member = ProjectMember.objects.filter(
            project=project,
            user=user,
            workspace_id=workspace_id,
            removed_at__isnull=True,
        ).first()

        if not is_creator and not member:
            # Mask project existence if from a foreign workspace the user does not belong to
            if str(project.workspace_id) != str(workspace_id):
                raise Http404("No Project matches the given query.")
            raise PermissionDenied("You do not have permission to access this project.")

        # Cache the results on the request object for serializing/view efficiency
        request._workspace_project_member_cache = {
            "project": project,
            "member": member,
            "is_creator": is_creator
        }

        return self._check_role(request, member, project, view)

    def _check_role(self, request, member, project, view):
        is_creator = project.created_by == request.user
        
        # Project creators have full bypass access
        if is_creator:
            return True

        # Determine the allowed roles for the request method
        if request.method in SAFE_METHODS:
            allowed_roles = getattr(view, "read_roles", self.default_read_roles)
        elif request.method == "DELETE":
            allowed_roles = getattr(view, "delete_roles", self.default_delete_roles)
        else: # POST, PATCH, PUT
            allowed_roles = getattr(view, "write_roles", self.default_write_roles)

        is_authorized = member and member.role in allowed_roles

        if not is_authorized:
            raise PermissionDenied("You do not have permission to perform this action.")

        return True
