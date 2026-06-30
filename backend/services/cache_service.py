import sqlite3
import hashlib
import os
import logging

logger = logging.getLogger(__name__)
CACHE_DB = "research_cache.db"

# Purge cache database once on module load
try:
    if os.path.exists(CACHE_DB):
        os.remove(CACHE_DB)
except Exception:
    pass

class CacheService:
    """
    Lightweight, persistent SQLite cache for LLM requests and search results.
    """
    @classmethod
    def _get_conn(cls):
        # Establish connection. Creates database file if it does not exist.
        conn = sqlite3.connect(CACHE_DB)
        conn.execute(
            "CREATE TABLE IF NOT EXISTS cache (key TEXT PRIMARY KEY, value TEXT, category TEXT)"
        )
        return conn

    @classmethod
    def get(cls, category: str, identifier: str) -> str | None:
        key = hashlib.md5(identifier.encode("utf-8")).hexdigest()
        try:
            with cls._get_conn() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT value FROM cache WHERE key = ? AND category = ?", 
                    (key, category)
                )
                row = cursor.fetchone()
                if row:
                    logger.info(f"Cache HIT for category '{category}'")
                    return row[0]
        except Exception as e:
            logger.error(f"Cache get failed: {e}")
        return None

    @classmethod
    def set(cls, category: str, identifier: str, value: str) -> None:
        key = hashlib.md5(identifier.encode("utf-8")).hexdigest()
        try:
            with cls._get_conn() as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO cache (key, value, category) VALUES (?, ?, ?)",
                    (key, value, category)
                )
        except Exception as e:
            logger.error(f"Cache set failed: {e}")
