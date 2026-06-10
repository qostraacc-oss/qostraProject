import jwt
import logging
from abc import ABC, abstractmethod
from django.conf import settings
from django.core.cache import cache
from rest_framework import authentication, exceptions

logger = logging.getLogger(__name__)

class BaseUserSyncService(ABC):
    """
    Abstract Service to handle user synchronization between the Auth service and 
    local project databases. Includes caching to prevent excessive DB hits.
    """
    
    @property
    @abstractmethod
    def model(self):
        """Must return the local User model class."""
        pass

    @property
    def cache_timeout(self):
        """Default cache timeout in seconds (1 hour)."""
        return 3600

    def get_cache_key(self, user_id):
        return f"auth_user_sync_{user_id}"

    def sync_user(self, user_id, token_payload):
        # 1. Check Cache first
        cache_key = self.get_cache_key(user_id)
        cached_user = cache.get(cache_key)
        if cached_user:
            return cached_user

        # 2. Sync with Database
        user_instance, created = self.model.objects.get_or_create(
            id=user_id
        )
        
        # Update local fields from payload
        if self.update_local_user(user_instance, token_payload) or created:
            user_instance.save()
            
        # 3. Store in Cache
        cache.set(cache_key, user_instance, timeout=self.cache_timeout)
        return user_instance

    @abstractmethod
    def update_local_user(self, user_instance, token_payload):
        """
        Logic to update project-specific fields from the token payload.
        Returns True if the instance was modified.
        """
        return False

class GenericJWTAuthentication(authentication.BaseAuthentication):
    """
    Generic DRF Authentication class that can be reused across projects.
    Expects a 'sync_service' property to be implemented in subclasses.
    """
    
    @property
    @abstractmethod
    def sync_service(self):
        """Must return an instance of BaseUserSyncService."""
        pass

    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header:
            return None

        try:
            prefix, token = auth_header.split(' ')
            if prefix.lower() != 'bearer':
                return None
        except ValueError:
            raise exceptions.AuthenticationFailed('Invalid token header.')

        # Decode Token
        try:
            payload = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=[getattr(settings, 'AUTH_ALGORITHM', 'HS256')]
            )
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token has expired.')
        except jwt.InvalidTokenError as e:
            logger.error(f"JWT Verification Failed: {str(e)}")
            raise exceptions.AuthenticationFailed('Invalid token.')

        user_id_claim = getattr(settings, 'AUTH_USER_ID_CLAIM', 'user_id')
        user_id = payload.get(user_id_claim)
        
        if not user_id:
            raise exceptions.AuthenticationFailed('Token missing user identification.')

        # Synchronize User using the project-specific service
        try:
            user = self.sync_service.sync_user(user_id, payload)
        except Exception as e:
            logger.exception("User synchronization failed")
            raise exceptions.AuthenticationFailed('User synchronization error.')

        return (user, token)
