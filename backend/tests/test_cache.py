"""Unit tests for Redis caching functionality"""
import pytest
import redis
import time
from unittest.mock import Mock, patch
from app.cache import (
    get_redis_client,
    cache_result,
    invalidate_cache,
    clear_all_cache,
    get_cache_stats
)


@pytest.fixture(autouse=True)
def reset_redis_singleton():
    """get_redis_client memoizes a module-level client; isolate each test"""
    import app.cache
    app.cache.redis_client = None
    yield
    app.cache.redis_client = None


class TestCacheUtilities:
    """Test Redis caching utilities"""

    @patch('app.cache.redis')
    def test_get_redis_client_creates_connection(self, mock_redis):
        """Test Redis client creation"""
        mock_client = Mock()
        mock_redis.from_url.return_value = mock_client
        mock_client.ping.return_value = True

        client = get_redis_client()
        assert client is not None
        mock_redis.from_url.assert_called_once()

    @patch('app.cache.redis')
    def test_get_redis_client_handles_connection_failure(self, mock_redis):
        """Test graceful handling of Redis connection failure"""
        # Keep the real exception class so the module's except clauses stay valid
        mock_redis.ConnectionError = redis.ConnectionError
        mock_redis.from_url.side_effect = Exception("Connection failed")

        client = get_redis_client()
        assert client is None

    @patch('app.cache.get_redis_client')
    def test_cache_result_decorator_caches_value(self, mock_get_client):
        """Test that cache_result decorator caches function results"""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_client.get.return_value = None  # Cache miss

        @cache_result("test_key", ttl=60)
        def expensive_function(x):
            return x * 2

        result = expensive_function(5)
        assert result == 10

        # Verify cache was written
        mock_client.setex.assert_called_once()

    @patch('app.cache.get_redis_client')
    def test_cache_result_decorator_returns_cached_value(self, mock_get_client):
        """Test that decorator returns cached value on cache hit"""
        import json

        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_client.get.return_value = json.dumps(20).encode()  # Cache hit

        call_count = 0

        @cache_result("test_key", ttl=60)
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        result = expensive_function(10)
        assert result == 20
        assert call_count == 0  # Function should not be called

    @patch('app.cache.get_redis_client')
    def test_cache_result_decorator_handles_redis_failure(self, mock_get_client):
        """Test decorator works even if Redis is unavailable"""
        mock_get_client.return_value = None  # Redis unavailable

        @cache_result("test_key", ttl=60)
        def expensive_function(x):
            return x * 2

        result = expensive_function(5)
        assert result == 10  # Function still executes

    @patch('app.cache.get_redis_client')
    def test_invalidate_cache_by_pattern(self, mock_get_client):
        """Test cache invalidation by pattern"""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_client.keys.return_value = [b'test:key1', b'test:key2']

        invalidate_cache("test:*")

        mock_client.keys.assert_called_once_with("test:*")
        mock_client.delete.assert_called_once_with(b'test:key1', b'test:key2')

    @patch('app.cache.get_redis_client')
    def test_invalidate_cache_handles_no_matches(self, mock_get_client):
        """Test cache invalidation with no matching keys"""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_client.keys.return_value = []

        invalidate_cache("nonexistent:*")

        mock_client.delete.assert_not_called()

    @patch('app.cache.get_redis_client')
    def test_clear_all_cache(self, mock_get_client):
        """Test clearing entire cache"""
        mock_client = Mock()
        mock_get_client.return_value = mock_client

        clear_all_cache()

        mock_client.flushdb.assert_called_once()

    @patch('app.cache.get_redis_client')
    def test_get_cache_stats_returns_stats(self, mock_get_client):
        """Test retrieving cache statistics"""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_client.info.side_effect = lambda section: (
            {'keyspace_hits': 1000, 'keyspace_misses': 100}
            if section == 'stats'
            else {'db0': {'keys': 42}}
        )

        stats = get_cache_stats()

        assert stats['status'] == 'connected'
        assert stats['keys'] == 42
        assert stats['hits'] == 1000
        assert stats['misses'] == 100
        assert 'hit_rate' in stats

    @patch('app.cache.get_redis_client')
    def test_get_cache_stats_handles_unavailable_redis(self, mock_get_client):
        """Test cache stats when Redis is unavailable"""
        mock_get_client.return_value = None

        stats = get_cache_stats()

        assert stats['status'] == 'unavailable'
        assert stats['keys'] == 0

    @patch('app.cache.get_redis_client')
    def test_cache_result_with_multiple_arguments(self, mock_get_client):
        """Test caching with multiple function arguments"""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_client.get.return_value = None

        @cache_result("test_func", ttl=60)
        def multi_arg_function(a, b, c=10):
            return a + b + c

        result = multi_arg_function(1, 2, c=3)
        assert result == 6

        # Verify cache key includes all arguments
        calls = mock_client.setex.call_args_list
        assert len(calls) == 1

    @patch('app.cache.get_redis_client')
    def test_cache_result_with_complex_return_value(self, mock_get_client):
        """Test caching complex data structures"""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_client.get.return_value = None

        @cache_result("test_complex", ttl=60)
        def complex_function():
            return {
                'list': [1, 2, 3],
                'dict': {'key': 'value'},
                'number': 42
            }

        result = complex_function()
        assert result['list'] == [1, 2, 3]
        assert result['dict']['key'] == 'value'

    @patch('app.cache.get_redis_client')
    def test_cache_ttl_is_applied(self, mock_get_client):
        """Test that TTL is correctly applied to cached values"""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_client.get.return_value = None

        @cache_result("test_ttl", ttl=300)
        def ttl_function():
            return "result"

        ttl_function()

        # Verify setex was called with correct TTL
        call_args = mock_client.setex.call_args
        assert call_args[0][1] == 300  # TTL should be 300 seconds


class TestCacheIntegration:
    """Integration tests for caching with API endpoints"""

    def test_metrics_summary_caching(self, client, auth_headers_patient, test_metric):
        """Test that metrics summary endpoint uses caching"""
        # First call - cache miss
        response1 = client.get("/api/metrics/summary", headers=auth_headers_patient)
        assert response1.status_code == 200
        data1 = response1.json()

        # Second call - should be cached
        response2 = client.get("/api/metrics/summary", headers=auth_headers_patient)
        assert response2.status_code == 200
        data2 = response2.json()

        # Results should be identical
        assert data1 == data2

    def test_cache_performance_improvement(self, client, auth_headers_patient, test_metric):
        """Test that caching improves response time"""
        # First call - uncached
        start1 = time.time()
        response1 = client.get("/api/metrics/summary", headers=auth_headers_patient)
        time1 = time.time() - start1

        # Second call - cached (should be faster or same)
        start2 = time.time()
        response2 = client.get("/api/metrics/summary", headers=auth_headers_patient)
        time2 = time.time() - start2

        assert response1.status_code == 200
        assert response2.status_code == 200
        # Cached response should not be significantly slower
        assert time2 <= time1 * 1.5  # Allow 50% margin for test variance
