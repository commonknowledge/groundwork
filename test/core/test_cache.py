from django.test import TestCase

from pyck.core.cache import cache, django_cached, django_cached_model_property


class CacheTestCase(TestCase):
    def test_gets_from_cache(self):
        @django_cached("test_gets_from_cache", get_key=lambda x: x)
        def cached_fn(x):
            cached_fn.num_calls += 1
            return cached_fn.num_calls

        cached_fn.num_calls = 0

        res = cached_fn(12)
        self.assertEqual(res, 1)
        self.assertIsNotNone(
            cache.get("test_gets_from_cache.12"), "uses expected cache key"
        )

        res = cached_fn(12)
        self.assertEqual(res, 1, "doesn’t refetch cached values")

        res = cached_fn(13)
        self.assertEqual(res, 2, "distinguishes between serialized parameters")

    def test_gets_from_cache_with_model_property(self):
        class SomeModel:
            id = "some_id"
            num_calls = 0

            @django_cached_model_property(
                "test_gets_from_cache", get_key=lambda self, x: x
            )
            def cached_fn(self, x):
                self.num_calls += 1
                return self.num_calls

        instance = SomeModel()

        res = instance.cached_fn(12)
        self.assertEqual(res, 1)
        self.assertIsNotNone(
            cache.get("test_gets_from_cache.some_id.12"), "uses expected cache key"
        )

        res = instance.cached_fn(12)
        self.assertEqual(res, 1, "doesn’t refetch cached values")

        res = instance.cached_fn(13)
        self.assertEqual(res, 2, "distinguishes between serialized parameters")
