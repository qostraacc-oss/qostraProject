from common.auth.core import GenericJWTAuthentication
from common.auth.user_sync import projects_user_sync_service


class ProjectsJWTAuthentication(GenericJWTAuthentication):
    """
    Projects-specific JWT Authentication.
    Uses ProjectsUserSyncService to handle user registration/caching.
    """

    @property
    def sync_service(self):
        return projects_user_sync_service


JWTAuthentication = ProjectsJWTAuthentication
