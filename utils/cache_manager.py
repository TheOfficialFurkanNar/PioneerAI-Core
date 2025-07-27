# utils/cache_manager.py

import os
import json
import functools
import time
from typing import Any, Callable, Dict, Tuple

# ----------------------------------------
# Dosya tabanlı basit cache
# ----------------------------------------
CACHE_DIR = "cache/"
os.makedirs(CACHE_DIR, exist_ok=True)

def save_cache(key: str, data: dict) -> None:
    """
    Veriyi JSON olarak CACHE_DIR içine kaydeder.
    """
    path = os.path.join(CACHE_DIR, f"{key}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_cache(key: str) -> dict:
    """
    CACHE_DIR içinden key’e karşılık gelen JSON’u yükler.
    Yoksa boş dict döner.
    """
    path = os.path.join(CACHE_DIR, f"{key}.json")
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# ----------------------------------------
# TTL cache dekoratörleri
# ----------------------------------------
def async_ttl_cache(ttl: int) -> Callable:
    """
    Asenkron fonksiyonları TTL (saniye) kadar cache’ler.
    """
    def decorator(func: Callable) -> Callable:
        cache: Dict[Tuple[Any, ...], Tuple[Any, float]] = {}

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            key = (args, tuple(sorted(kwargs.items())))
            result, ts = cache.get(key, (None, 0.0))
            if time.monotonic() - ts < ttl:
                return result
            result = await func(*args, **kwargs)
            cache[key] = (result, time.monotonic())
            return result

        return wrapper
    return decorator

def sync_ttl_cache(ttl: int) -> Callable:
    """
    Eşzamanlı fonksiyonları TTL (saniye) kadar cache’ler.
    """
    def decorator(func: Callable) -> Callable:
        cache: Dict[Tuple[Any, ...], Tuple[Any, float]] = {}

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = (args, tuple(sorted(kwargs.items())))
            result, ts = cache.get(key, (None, 0.0))
            if time.monotonic() - ts < ttl:
                return result
            result = func(*args, **kwargs)
            cache[key] = (result, time.monotonic())
            return result

        return wrapper
    return decorator