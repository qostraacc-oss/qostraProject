import logging
from django.core.cache import cache

logger = logging.getLogger(__name__)

def get_or_set_cached(cache_key, fetch_func, timeout=300, *args, **kwargs):
    """
    Gets a value from the cache. If it doesn't exist, invokes the fallback function,
    caches the returned value (if not None), and returns it.
    
    Args:
        cache_key (str): The cache key to lookup/store.
        fetch_func (callable): The function to fetch the data if cache misses.
        timeout (int): Cache TTL in seconds.
        *args: Variable arguments for fetch_func.
        **kwargs: Keyword arguments for fetch_func.
    """
    cached_value = cache.get(cache_key)
    if cached_value is not None:
        logger.debug(f"Cache hit for key: {cache_key}")
        return cached_value

    logger.debug(f"Cache miss for key: {cache_key}. Invoking fallback function.")
    result = fetch_func(*args, **kwargs)
    
    if result is not None:
        cache.set(cache_key, result, timeout=timeout)
        
    return result
