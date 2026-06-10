import logging
from django.contrib.auth import get_user_model
from django.core.cache import cache
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
        # 1. Check Cache first
        cache_key = self.get_cache_key(user_id)
        cached_user = cache.get(cache_key)
        if cached_user:
            return cached_user

        # 2. Sync with Database
        default_username = token_payload.get('username') or token_payload.get('email') or user_id
        user_instance, created = self.model.objects.get_or_create(
            id=user_id,
            defaults={'username': default_username}
        )
        
        # Update local fields from payload
        if self.update_local_user(user_instance, token_payload) or created:
            user_instance.save()
            
        # 3. Store in Cache
        cache.set(cache_key, user_instance, timeout=self.cache_timeout)
        return user_instance

    def update_local_user(self, user_instance, token_payload):
        """
        Updates the local User model instance with claims present in the JWT payload.
        """
        modified = False
        email = token_payload.get('email')
        first_name = token_payload.get('first_name')
        last_name = token_payload.get('last_name')
        username = token_payload.get('username') or email

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
