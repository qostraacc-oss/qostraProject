import requests
import logging
from django.conf import settings
from rest_framework import serializers
from common.utils.cache import get_or_set_cached

logger = logging.getLogger(__name__)


def lookup_user_by_email(email, auth_header=None):
    """
    Looks up a user's details (UUID, email, etc.) from the Auth service by email.
    Uses caching to avoid redundant requests.

    Raises:
        serializers.ValidationError: If the user is not found or validation fails.
    """
    if not email:
        raise serializers.ValidationError({"email": "Email is required for lookup."})

    cache_key = f"auth_user_lookup:{email.lower()}"
    cache_ttl = getattr(
        settings, "DIRECTORY_CLIENT_CACHE_TTL", 300
    )  # Reuse TTL or default to 5 mins

    def _fetch_user():
        auth_url = getattr(settings, "AUTH_SERVICE_URL", "http://127.0.0.1:8100")
        url = f"{auth_url.rstrip('/')}/users/lookup/"

        headers = {}
        if auth_header:
            headers["Authorization"] = auth_header

        try:
            response = requests.get(
                url, params={"email": email}, headers=headers, timeout=5
            )

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None
            else:
                logger.warning(
                    f"Auth service user lookup returned status: {response.status_code}"
                )
                raise serializers.ValidationError(
                    {
                        "email": "Unable to validate user with the authentication service. "
                        "Please try again later."
                    }
                )

        except requests.ConnectionError:
            logger.error(
                "Auth service is unreachable. Ensure the Auth server is running."
            )
            raise serializers.ValidationError(
                {
                    "email": "Unable to reach the authentication service. "
                    "Please try again shortly or contact support."
                }
            )
        except requests.Timeout:
            logger.error("Auth service request timed out.")
            raise serializers.ValidationError(
                {
                    "email": "The authentication service is taking too long to respond. "
                    "Please try again."
                }
            )
        except requests.RequestException as e:
            logger.error(f"Auth service communication error: {e}")
            raise serializers.ValidationError(
                {
                    "email": "An unexpected error occurred while validating the user. "
                    "Please try again later."
                }
            )

    # Query or cache
    user_data = get_or_set_cached(cache_key, _fetch_user, timeout=cache_ttl)

    if not user_data:
        raise serializers.ValidationError(
            {"email": "No Qostra user exists with this email address."}
        )

    return user_data
