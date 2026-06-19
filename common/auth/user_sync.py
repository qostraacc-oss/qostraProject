import logging
from django.contrib.auth import get_user_model
from common.auth.core import BaseUserSyncService

logger = logging.getLogger(__name__)
User = get_user_model()


class ProjectsUserSyncService(BaseUserSyncService):
    """
    Projects User Sync Service.
    Maps user information from the QostraAuth JWT token to the local User model.
    """

    @property
    def model(self):
        return User

    def sync_user(self, user_id, token_payload):
        from common.utils.cache import get_or_set_cached

        cache_key = self.get_cache_key(user_id)

        def _db_sync():
            default_username = (
                token_payload.get("username") or token_payload.get("email") or user_id
            )
            user_instance, created = self.model.objects.get_or_create(
                id=user_id, defaults={"username": default_username}
            )
            if self.update_local_user(user_instance, token_payload) or created:
                user_instance.save()
            return user_instance

        return get_or_set_cached(cache_key, _db_sync, timeout=self.cache_timeout)

    def update_local_user(self, user_instance, token_payload):
        """
        Updates the local User model instance with claims present in the JWT payload.
        """
        modified = False
        email = token_payload.get("email")
        first_name = token_payload.get("first_name")
        last_name = token_payload.get("last_name")
        username = token_payload.get("username") or email

        if username and user_instance.username != username:
            user_instance.username = username
            modified = True

        if email and user_instance.email != email:
            user_instance.email = email
            modified = True

        if first_name and user_instance.first_name != first_name:
            user_instance.first_name = first_name
            modified = True

        if last_name and user_instance.last_name != last_name:
            user_instance.last_name = last_name
            modified = True

        return modified


projects_user_sync_service = ProjectsUserSyncService()
