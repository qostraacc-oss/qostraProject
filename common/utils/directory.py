import requests
import logging
from django.conf import settings
from rest_framework import serializers
from common.utils.cache import get_or_set_cached

logger = logging.getLogger(__name__)

def validate_directory_client(workspace_id, client_id, auth_header=None):
    """
    Validates a client_id against the Directory service for a given workspace_id.
    Uses generic caching to avoid redundant external network requests.
    
    Raises:
        serializers.ValidationError: If validation fails or client is invalid/inactive.
    """
    if not client_id or not workspace_id:
        return

    cache_key = f"dir_client_val:{workspace_id}:{client_id}"
    cache_ttl = getattr(settings, 'DIRECTORY_CLIENT_CACHE_TTL', 300)

    def _fetch_validity():
        directory_url = getattr(settings, 'DIRECTORY_SERVICE_URL', 'http://127.0.0.1:8002')
        url = f"{directory_url.rstrip('/')}/workspaces/{workspace_id}/clients/{client_id}/"
        
        headers = {}
        if auth_header:
            headers['Authorization'] = auth_header

        try:
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                return True
            elif response.status_code == 404:
                return False
            else:
                logger.warning(f"Directory service client validation returned status: {response.status_code}")
                raise serializers.ValidationError({
                    'client_id': 'Unable to validate client ID with Directory service.'
                })
                
        except requests.RequestException as e:
            logger.error(f"Failed to communicate with Directory service: {str(e)}")
            raise serializers.ValidationError({
                'client_id': f'Directory service validation failed: {str(e)}'
            })

    # Call the generic caching utility
    is_valid = get_or_set_cached(cache_key, _fetch_validity, timeout=cache_ttl)
    
    if not is_valid:
        raise serializers.ValidationError({
            'client_id': 'Client does not exist in this workspace or is inactive.'
        })
