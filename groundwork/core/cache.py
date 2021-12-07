from typing import Any, Callable, TypeVar

from django.core.cache import cache
from django.db.models import QuerySet

from groundwork.core.types import Decorator


def django_cached(prefix: str, get_key: Any = None, ttl: int = 500) -> Decorator:
    """
    Decorator to cache a function using the default cache.

    Args:
        get_key: Return a cache key given the arguments to the function
        prefix: Prefix applied to the cache key
        ttl: TTL in seconds

    Returns:
        A function decorator
    """

    def decorator(fn):
        def cached_fn(*args, **kwargs):
            key = prefix
            if get_key != None:
                key += "." + str(get_key(*args, **kwargs))

            hit = cache.get(key)
            if hit is None:
                hit = fn(*args, **kwargs)
                if isinstance(hit, QuerySet):
                    hit = tuple(hit[:10000])

                cache.set(key, hit, ttl)

            return hit

        return cached_fn

    return decorator


def django_cached_model_property(
    prefix: str, get_key: Any = None, ttl: int = 500
) -> Decorator:
    """
    Decorator to cache a model method using the default cache, scoped to the model instance.

    Args:
        get_key: Return a cache key given the arguments to the function
        prefix: Prefix applied to the cache key
        ttl: TTL in seconds

    Returns:
        A method decorator
    """

    if get_key is None:
        get_key_on_model = lambda self, *args, **kargs: self.id
    else:
        get_key_on_model = (
            lambda self, *args, **kwargs: f"{self.id}.{get_key(self, *args, **kwargs)}"
        )

    return django_cached(prefix, get_key=get_key_on_model, ttl=ttl)
