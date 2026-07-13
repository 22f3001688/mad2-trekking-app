import json
import logging
from datetime import date
from urllib.parse import quote_plus

import redis
from flask import current_app, has_app_context


logger = logging.getLogger(__name__)

TREK_BROWSE_CACHE_PREFIX = "trekscape:cache:treks:browse"


class CacheService:
    def __init__(self):
        self._redis_client = None

    def _get_logger(self):
        if has_app_context():
            return current_app.logger
        return logger

    def _get_client(self):
        if self._redis_client is not None:
            return self._redis_client

        if has_app_context():
            cache_extensions = current_app.extensions.setdefault("trekscape_cache", {})
            client = cache_extensions.get("redis_client")
            if client is None:
                redis_url = current_app.config.get("CACHE_REDIS_URL", "redis://localhost:6379/2")
                client = redis.Redis.from_url(
                    redis_url,
                    decode_responses=True,
                    socket_connect_timeout=0.5,
                    socket_timeout=0.5,
                    retry_on_timeout=False,
                )
                cache_extensions["redis_client"] = client
            return client

        self._redis_client = redis.Redis.from_url(
            "redis://localhost:6379/2",
            decode_responses=True,
            socket_connect_timeout=0.5,
            socket_timeout=0.5,
            retry_on_timeout=False,
        )
        return self._redis_client

    def _get_ttl(self):
        if has_app_context():
            ttl_value = current_app.config.get("TREK_CACHE_TTL", 300)
        else:
            ttl_value = 300

        try:
            ttl = int(ttl_value)
        except (TypeError, ValueError):
            ttl = 300

        return max(ttl, 1)

    def get_json(self, key):
        try:
            raw_value = self._get_client().get(key)
            if raw_value is None:
                return None
            return json.loads(raw_value)
        except Exception as exc:
            self._get_logger().warning("Redis cache read failed for %s: %s", key, exc)
            return None

    def set_json(self, key, value, ttl=None):
        try:
            serialized_value = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
            expiry = self._get_ttl() if ttl is None else max(int(ttl), 1)
            self._get_client().set(key, serialized_value, ex=expiry)
            return True
        except Exception as exc:
            self._get_logger().warning("Redis cache write failed for %s: %s", key, exc)
            return False

    def delete(self, key):
        try:
            self._get_client().delete(key)
            return True
        except Exception as exc:
            self._get_logger().warning("Redis cache delete failed for %s: %s", key, exc)
            return False

    def delete_by_prefix(self, prefix):
        try:
            redis_client = self._get_client()
            for key in redis_client.scan_iter(match=f"{prefix}*", count=200):
                redis_client.delete(key)
            return True
        except Exception as exc:
            self._get_logger().warning("Redis cache prefix invalidation failed for %s: %s", prefix, exc)
            return False


cache_service = CacheService()


def normalize_trek_browse_filters(filters=None):
    filters = filters or {}
    normalized_filters = {
        "q": (filters.get("q") or "").strip().lower(),
        "difficulty": (filters.get("difficulty") or "").strip().lower(),
        "location": (filters.get("location") or "").strip().lower(),
        "sort": (filters.get("sort") or "start_asc").strip().lower() or "start_asc",
    }

    duration_value = (filters.get("duration") or "").strip()
    if duration_value:
        normalized_filters["duration"] = str(int(duration_value))
    else:
        normalized_filters["duration"] = ""

    return normalized_filters


def build_trek_browse_cache_key(trekker_user_id, filters=None, browse_date=None):
    normalized_filters = normalize_trek_browse_filters(filters)
    browse_date = browse_date or date.today().isoformat()

    return (
        f"{TREK_BROWSE_CACHE_PREFIX}:user:{trekker_user_id}:date:{browse_date}:"
        f"q:{quote_plus(normalized_filters['q'])}:"
        f"difficulty:{quote_plus(normalized_filters['difficulty'])}:"
        f"location:{quote_plus(normalized_filters['location'])}:"
        f"duration:{quote_plus(normalized_filters['duration'])}:"
        f"sort:{quote_plus(normalized_filters['sort'])}"
    )


def invalidate_trek_browse_cache():
    return cache_service.delete_by_prefix(TREK_BROWSE_CACHE_PREFIX)